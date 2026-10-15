"""
Generate a browser-console script that downloads book covers using your own
normal Chrome (which has already passed Cloudflare verification).

Usage:
    py -3.13 make_console_js.py
Then open console_download.js, copy everything, and paste it into the DevTools
Console of a normal Chrome tab that is showing a cover image from the site.

A folder picker pops up: choose the LOG_DIR folder (e.g. Bookcover).
- Images are written into SAVE_DIR (e.g. Bookcover/covers); existing ones are skipped.
- A report CSV (download_report_*.csv) listing every ISBN and its result is
  written into LOG_DIR.
"""
import csv
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")
load_dotenv()

SITE = os.getenv("SITE", "bookdepot").lower()
CSV_FILE = os.getenv("CSV_FILE")
SAVE_DIR = Path(os.getenv("SAVE_DIR", "."))
LOG_DIR = Path(os.getenv("LOG_DIR") or SAVE_DIR.parent)
MIN_IMAGE_SIZE = 5000
OUT_FILE = Path("console_download.js")

SITE_HOSTS = {
    "bookdepot": {"images.bookdepot.com"},
    "bookoutlet": {"bookoutlet.com", "www.bookoutlet.com"},
}

if not CSV_FILE:
    raise ValueError("CSV_FILE 未配置")
if SITE not in SITE_HOSTS:
    raise ValueError(f"不支持的站点: {SITE}")
hosts = SITE_HOSTS[SITE]

# SAVE_DIR 相对 LOG_DIR 的子路径：选 LOG_DIR 后，脚本自动进入这个子文件夹
try:
    subdirs = list(SAVE_DIR.resolve().relative_to(LOG_DIR.resolve()).parts)
    pick_folder = LOG_DIR
except ValueError:
    subdirs = None  # SAVE_DIR 不在 LOG_DIR 下：直接选 SAVE_DIR，报告走浏览器下载
    pick_folder = SAVE_DIR


def extract_isbn(url):
    m = re.search(r"(97[89]\d{10})", url)
    return m.group(1) if m else None


items, seen = [], set()
counts = {"PENDING": 0, "EXISTS": 0, "SKIPPED": 0}

with open(CSV_FILE, newline="", encoding="utf-8-sig") as f:
    for row in csv.reader(f):
        if not row:
            continue
        url = row[0].strip()
        if not url or url.lower() in ("image", "图片"):
            continue
        md = re.search(r"\]\((https?://[^)]+)\)", url)
        if md:
            url = md.group(1)
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        url = url.replace("http://", "https://", 1)

        isbn = extract_isbn(url) or ""
        item = {"isbn": isbn, "url": url, "status": "", "size": "", "detail": "", "time": ""}

        if urlparse(url).hostname not in hosts:
            item.update(status="SKIPPED", detail="域名不符合当前站点")
        elif not isbn:
            item.update(status="SKIPPED", detail="无法提取ISBN")
        elif isbn in seen:
            item.update(status="SKIPPED", detail="CSV中重复")
        else:
            seen.add(isbn)
            existing = SAVE_DIR / f"{isbn}.jpg"
            if existing.exists() and existing.stat().st_size > MIN_IMAGE_SIZE:
                item.update(status="EXISTS", size=existing.stat().st_size, detail="运行前已存在")
            else:
                item.update(status="PENDING")

        counts[item["status"]] += 1
        items.append(item)

js = f"""(async () => {{
  const items = {json.dumps(items, ensure_ascii=False, indent=0)};
  const SUBDIRS = {json.dumps(subdirs, ensure_ascii=False)};
  const MIN_SIZE = {MIN_IMAGE_SIZE};
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const now = () => new Date().toLocaleString("sv-SE");
  const stamp = now().replace(/[-: ]/g, "").replace(/^(\\d{{8}})/, "$1_");

  console.log("请选择文件夹:", {json.dumps(str(pick_folder), ensure_ascii=False)});

  // 选择文件夹；取消则图片和报告都改为保存到浏览器"下载"文件夹
  let root = null, out = null;
  try {{
    root = await window.showDirectoryPicker({{ id: "bookcover-root", mode: "readwrite" }});
    out = root;
    for (const p of (SUBDIRS || [])) out = await out.getDirectoryHandle(p, {{ create: true }});
    console.log("报告目录:", root.name, " 图片目录:", out.name);
  }} catch (e) {{
    console.warn("未选择文件夹，改为保存到浏览器的下载文件夹", e);
  }}

  function browserDownload(name, blob) {{
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = name;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 15000);
  }}

  async function writeFile(dir, name, blob) {{
    if (!dir) return browserDownload(name, blob);
    const w = await (await dir.getFileHandle(name, {{ create: true }})).createWritable();
    await w.write(blob);
    await w.close();
  }}

  async function existingSize(name) {{
    if (!out) return 0;
    try {{ return (await (await out.getFileHandle(name)).getFile()).size; }}
    catch {{ return 0; }}
  }}

  const pending = items.filter(it => it.status === "PENDING");
  let ok = 0, skip = 0, consecutiveFail = 0, stopped = false;

  for (const [i, it] of pending.entries()) {{
    const name = it.isbn + ".jpg";
    const tag = `[${{i + 1}}/${{pending.length}}]`;

    if (stopped) {{ it.status = "NOT_RUN"; it.detail = "提前停止，未处理"; continue; }}

    const have = await existingSize(name);
    if (have > MIN_SIZE) {{
      Object.assign(it, {{ status: "EXISTS", size: have, detail: "文件夹中已存在", time: now() }});
      skip++;
      continue;
    }}

    try {{
      const r = await fetch(it.url, {{ credentials: "include", cache: "no-store" }});
      const ct = r.headers.get("content-type") || "";
      it.time = now();
      if (r.status === 403 || r.headers.get("cf-mitigated") === "challenge") {{
        Object.assign(it, {{ status: "CF_BLOCKED", detail: `Status=${{r.status}}` }});
        console.error(tag, "Cloudflare 403 — 刷新本页通过验证后，重新粘贴运行即可续传");
        stopped = true;
        continue;
      }}
      if (!r.ok || !ct.startsWith("image/")) {{
        Object.assign(it, {{ status: "FAIL", detail: `Status=${{r.status}} Type=${{ct}}` }});
        console.warn(tag, "FAIL", it.isbn, r.status, ct);
        consecutiveFail++;
      }} else {{
        const blob = await r.blob();
        if (blob.size <= MIN_SIZE) {{
          Object.assign(it, {{ status: "FAIL", size: blob.size, detail: "图片过小" }});
          console.warn(tag, "TOO SMALL", it.isbn, blob.size);
          consecutiveFail++;
        }} else {{
          await writeFile(out, name, blob);
          Object.assign(it, {{ status: "OK", size: blob.size, detail: "" }});
          ok++;
          consecutiveFail = 0;
          console.log(tag, "OK", it.isbn, blob.size);
        }}
      }}
    }} catch (e) {{
      Object.assign(it, {{ status: "ERROR", detail: String(e), time: now() }});
      console.warn(tag, "ERROR", it.isbn, e);
      consecutiveFail++;
    }}

    if (consecutiveFail >= 10) {{
      console.error("连续失败 10 次，停止");
      stopped = true;
      continue;
    }}
    await sleep(800 + Math.random() * 700);
  }}

  // ===== 生成清单 CSV =====
  const cols = ["isbn", "url", "status", "size", "detail", "time"];
  const cell = v => {{
    const s = String(v ?? "");
    return /[",\\r\\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
  }};
  const csvText = "\\uFEFF" + [cols, ...items.map(it => cols.map(c => it[c]))]
    .map(row => row.map(cell).join(",")).join("\\r\\n");
  const reportName = `download_report_${{stamp}}.csv`;
  const reportDir = SUBDIRS ? root : null;
  try {{
    await writeFile(reportDir, reportName, new Blob([csvText], {{ type: "text/csv" }}));
    console.log("清单已保存:", reportDir ? `${{root.name}}/${{reportName}}` : `下载文件夹/${{reportName}}`);
  }} catch (e) {{
    console.warn("清单写入失败，改为浏览器下载", e);
    browserDownload(reportName, new Blob([csvText], {{ type: "text/csv" }}));
  }}

  const by = s => items.filter(it => it.status === s).length;
  console.log(`DONE  成功=${{ok}}  已存在=${{by("EXISTS")}}  失败=${{by("FAIL") + by("ERROR")}}  ` +
              `CF拦截=${{by("CF_BLOCKED")}}  未处理=${{by("NOT_RUN")}}  跳过=${{by("SKIPPED")}}`);
  const failed = items.filter(it => ["FAIL", "ERROR", "CF_BLOCKED"].includes(it.status));
  if (failed.length) console.log("失败的ISBN:\\n" + failed.map(it => it.isbn).join("\\n"));
}})();
"""

OUT_FILE.write_text(js, encoding="utf-8")

# ===== ISBN + URL 清单（CSV 中所有有效且不重复的条目）=====
from datetime import datetime

list_file = LOG_DIR / f"isbn_url_list_{datetime.now():%Y%m%d_%H%M%S}.csv"
LOG_DIR.mkdir(parents=True, exist_ok=True)
with open(list_file, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["isbn", "url"])
    for it in items:
        if it["status"] in ("PENDING", "EXISTS"):
            w.writerow([it["isbn"], it["url"]])

print(f"[OK] ISBN清单: {list_file}")
print(
    f"[OK] 待下载: {counts['PENDING']} | 已存在: {counts['EXISTS']} | "
    f"跳过(域名/ISBN/重复): {counts['SKIPPED']}"
)
print(f"[OK] 已生成: {OUT_FILE.resolve()}")
print(f"[提示] 运行时请选择文件夹: {pick_folder}")