"""
Book cover downloader — real Chrome edition.

Chrome (driven by Playwright) fetches every image, so UA / TLS fingerprint /
IP / cookies always match. When Cloudflare shows a verification page, the
script pauses and waits for you to complete it in the Chrome window.

.env:
    SITE=bookdepot              # or bookoutlet
    CSV_FILE=...
    SAVE_DIR=...
    LOG_DIR=...
    PROFILE_DIR=chrome_profile  # optional, dedicated Chrome profile
    DELAY_MIN=0.8               # optional
    DELAY_MAX=1.5               # optional
"""
import base64
import csv
import os
import random
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")

# ========== 读取 .env ==========
load_dotenv()

SITE = os.getenv("SITE", "bookdepot").lower()
csv_file_path = os.getenv("CSV_FILE")
save_dir_value = os.getenv("SAVE_DIR")
log_dir_value = os.getenv("LOG_DIR")
PROFILE_DIR = Path(os.getenv("PROFILE_DIR", "chrome_profile")).resolve()
DELAY_MIN = float(os.getenv("DELAY_MIN", "0.8"))
DELAY_MAX = float(os.getenv("DELAY_MAX", "1.5"))

if not all([csv_file_path, save_dir_value, log_dir_value]):
    raise ValueError("CSV_FILE / SAVE_DIR / LOG_DIR 未配置")

save_dir = Path(save_dir_value)
log_dir = Path(log_dir_value)
save_dir.mkdir(parents=True, exist_ok=True)
log_dir.mkdir(parents=True, exist_ok=True)

# ========== 站点配置 ==========
SITE_CONFIG = {
    "bookoutlet": {"hosts": {"bookoutlet.com", "www.bookoutlet.com"}},
    "bookdepot": {"hosts": {"images.bookdepot.com"}},
}
if SITE not in SITE_CONFIG:
    raise ValueError(f"不支持的站点: {SITE}")
config = SITE_CONFIG[SITE]

MIN_IMAGE_SIZE = 5000
MAX_CONSECUTIVE_FAIL = 10
VERIFY_TIMEOUT = 300  # 等待你完成验证的最长秒数

run_stamp = f"{datetime.now():%Y%m%d_%H%M%S}"
log_file = log_dir / f"download_log_{run_stamp}.txt"
failed_file = log_dir / f"failed_{run_stamp}.csv"


# ========== 工具函数 ==========
def extract_isbn(url):
    m = re.search(r"/(97[89]\d{10})-l\.jpg", url) or re.search(r"(97[89]\d{10})", url)
    return m.group(1) if m else None


def read_urls(path):
    urls = []
    with open(path, newline="", encoding="utf-8-sig") as f:
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
            urls.append(url)
    return urls


log_lines = []


def write_log(message):
    print(message)
    log_lines.append(message)


# 在页面内用浏览器自己的 fetch 下载图片，返回 base64
JS_FETCH = """
async (url) => {
  try {
    const r = await fetch(url, { credentials: "include", cache: "no-store" });
    const ct = r.headers.get("content-type") || "";
    const mitig = r.headers.get("cf-mitigated") || "";
    if (!r.ok || !ct.startsWith("image/")) {
      return { status: r.status, ct, mitig, b64: null, size: 0 };
    }
    const bytes = new Uint8Array(await r.arrayBuffer());
    let bin = "";
    for (let i = 0; i < bytes.length; i += 0x8000) {
      bin += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
    }
    return { status: r.status, ct, mitig, b64: btoa(bin), size: bytes.length };
  } catch (e) {
    return { status: 0, ct: "", mitig: "", b64: null, size: 0, error: String(e) };
  }
}
"""


def on_challenge(page):
    """当前页面是否是 Cloudflare 验证页"""
    try:
        if "just a moment" in page.title().lower():
            return True
        return page.locator(
            "iframe[src*='challenges.cloudflare.com'], #challenge-form"
        ).count() > 0
    except Exception:
        # 页面正在跳转（比如刚点完验证），当作还没好
        return True


def ensure_verified(page, url):
    """打开 url；如遇验证，暂停等你在窗口里完成"""
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(1500)
    if not on_challenge(page):
        return True

    print("\n========== Cloudflare 验证 ==========")
    print("请在弹出的 Chrome 窗口中点击 'Verify you are human'。")
    print(f"脚本会自动检测，最多等待 {VERIFY_TIMEOUT} 秒。")
    print("=====================================")

    deadline = time.time() + VERIFY_TIMEOUT
    while time.time() < deadline:
        page.wait_for_timeout(2000)
        if not on_challenge(page):
            print("[OK] 验证通过，继续下载\n")
            page.wait_for_timeout(1000)
            return True
    return False


# ========== 主流程 ==========
def main():
    all_urls = read_urls(csv_file_path)
    stats = {"ok": 0, "skip": 0, "fail": 0, "error": 0}
    failed_rows = []

    # 预过滤：域名、ISBN、去重、已存在
    tasks, seen = [], set()
    for url in all_urls:
        isbn = extract_isbn(url)
        parsed = urlparse(url)
        if not isbn:
            write_log(f"[SKIP] 无法提取ISBN: {url}")
            stats["skip"] += 1
            continue
        if parsed.scheme != "https" or parsed.hostname not in config["hosts"]:
            write_log(f"[SKIP] URL域名或协议不符合当前站点: {url}")
            stats["skip"] += 1
            continue
        if isbn in seen:
            stats["skip"] += 1
            continue
        seen.add(isbn)
        fp = save_dir / f"{isbn}.jpg"
        if fp.exists() and fp.stat().st_size > MIN_IMAGE_SIZE:
            stats["skip"] += 1
            continue
        tasks.append((isbn, url))

    write_log(f"[INFO] 站点: {SITE}")
    write_log(f"[INFO] CSV共 {len(all_urls)} 个URL，待下载 {len(tasks)}，跳过 {stats['skip']}")

    if not tasks:
        return stats, failed_rows, False

    stopped = False

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            channel="chrome",
            headless=False,
            viewport={"width": 1100, "height": 800},
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        try:
            # 先打开第一张图，确保处在图片域名下并通过验证
            if not ensure_verified(page, tasks[0][1]):
                write_log("[STOP] 等待验证超时")
                return stats, failed_rows, True

            consecutive_fail = 0
            i = 0
            while i < len(tasks):
                isbn, url = tasks[i]
                progress = f"[{i + 1}/{len(tasks)}]"
                file_path = save_dir / f"{isbn}.jpg"

                res = page.evaluate(JS_FETCH, url)

                # 被验证拦截：暂停等你验证，然后重试当前这张
                if res["status"] == 403 or res["mitig"] == "challenge":
                    write_log(f"{progress} [CF] {isbn} 需要重新验证")
                    if ensure_verified(page, url):
                        continue
                    write_log("[STOP] 等待验证超时")
                    stopped = True
                    break

                if res.get("error"):
                    write_log(f"{progress} [ERROR] {isbn} {res['error']}")
                    stats["error"] += 1
                    failed_rows.append((isbn, url, res["error"]))
                    consecutive_fail += 1
                elif res["b64"] is None:
                    reason = f"Status={res['status']} Type={res['ct']}"
                    write_log(f"{progress} [FAIL] {isbn} {reason}")
                    stats["fail"] += 1
                    failed_rows.append((isbn, url, reason))
                    consecutive_fail += 1
                elif res["size"] <= MIN_IMAGE_SIZE:
                    reason = f"图片过小 {res['size']} bytes"
                    write_log(f"{progress} [FAIL] {isbn} {reason}")
                    stats["fail"] += 1
                    failed_rows.append((isbn, url, reason))
                    consecutive_fail += 1
                else:
                    data = base64.b64decode(res["b64"])
                    temp_path = file_path.with_suffix(".jpg.part")
                    temp_path.write_bytes(data)
                    temp_path.replace(file_path)
                    write_log(f"{progress} [OK] {isbn} ({len(data)} bytes)")
                    stats["ok"] += 1
                    consecutive_fail = 0

                if consecutive_fail >= MAX_CONSECUTIVE_FAIL:
                    write_log(f"[STOP] 连续失败 {MAX_CONSECUTIVE_FAIL} 次，停止以免被封")
                    stopped = True
                    break

                i += 1
                time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

        except KeyboardInterrupt:
            write_log("[STOP] 手动中断")
            stopped = True
        finally:
            ctx.close()

    return stats, failed_rows, stopped


if __name__ == "__main__":
    started = datetime.now()
    stats, failed_rows, stopped = main()

    if failed_rows:
        with open(failed_file, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["isbn", "url", "reason"])
            w.writerows(failed_rows)

    summary = (
        f"\n{'=' * 50}\n"
        f"开始: {started:%Y-%m-%d %H:%M:%S}  结束: {datetime.now():%Y-%m-%d %H:%M:%S}\n"
        f"成功: {stats['ok']} | 跳过: {stats['skip']} | "
        f"失败: {stats['fail']} | 错误: {stats['error']}\n"
        f"提前停止: {stopped}\n"
        + (f"失败清单: {failed_file}\n" if failed_rows else "")
    )
    write_log(summary)
    log_file.write_text("\n".join(log_lines), encoding="utf-8")
    print(f"[LOG] 日志已保存: {log_file}")
    print("[DONE] 程序结束（重新运行只会下载还缺的封面）")