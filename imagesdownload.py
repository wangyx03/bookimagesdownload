import sys
sys.stdout.reconfigure(encoding="utf-8")

import csv
import re
import requests
from pathlib import Path
from dotenv import load_dotenv
import os
from datetime import datetime

# ========== 读取 .env ==========
load_dotenv()
SITE = os.getenv("SITE", "bookdepot").lower()
CF_CLEARANCE = os.getenv("CF_CLEARANCE") if SITE == "bookdepot" else None

# ========== 配置 ==========
SITE_CONFIG = {
    "bookoutlet": {
        "referer": "https://www.bookoutlet.com/",
        "csv_file": r"D:\book images\bookimages.csv",
        "save_dir": r"D:\book images\covers",
    },
    "bookdepot": {
        "referer": "https://images.bookdepot.com/",
        "csv_file": r"D:\book images\bookimages.csv",
        "save_dir": r"D:\book images\covers",
    },
}

if SITE not in SITE_CONFIG:
    raise ValueError(f"SITE 配置错误，只支持: {list(SITE_CONFIG.keys())}")

config = SITE_CONFIG[SITE]
csv_file_path = config["csv_file"]
save_dir = Path(config["save_dir"])
save_dir.mkdir(parents=True, exist_ok=True)

log_file = save_dir / f"download_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

headers = {
    #注意同步版本号#
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    "Referer": config["referer"],
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
}

cookies = {"cf_clearance": CF_CLEARANCE} if CF_CLEARANCE else {}

print(f"[INFO] 当前站点: {SITE} | Referer: {config['referer']}")

# ========== 提取 ISBN ==========
def extract_isbn(url):
    m = re.search(r"/(97[89]\d{10})-l\.jpg", url)
    if m:
        return m.group(1)
    m = re.search(r"(97[89]\d{10})", url)
    if m:
        return m.group(1)
    return None

# ========== 读取 CSV ==========
urls = []

with open(csv_file_path, newline="", encoding="utf-8-sig") as f:
    reader = csv.reader(f)
    for row in reader:
        if not row:
            continue
        url = row[0].strip()
        if url.lower() in ("image", "图片"):
            continue
        urls.append(url)

print(f"[OK] 共读取 {len(urls)} 个URL")

# ========== 下载 ==========
session = requests.Session()

stats = {"ok": 0, "skip": 0, "fail": 0, "error": 0}
log_lines = [
    f"站点: {SITE}",
    f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    f"CSV: {csv_file_path}",
    f"总URL数: {len(urls)}",
    "-" * 50,
]

for url in urls:
    url = "https://" + url if not url.startswith("http") else url
    isbn = extract_isbn(url)

    if not isbn:
        msg = f"[SKIP] 无法提取ISBN: {url}"
        print(msg)
        log_lines.append(msg)
        stats["skip"] += 1
        continue

    file_path = save_dir / f"{isbn}.jpg"

    if file_path.exists() and file_path.stat().st_size > 5000:
        msg = f"[SKIP] 已存在: {isbn}"
        print(msg)
        log_lines.append(msg)
        stats["skip"] += 1
        continue

    try:
        r = session.get(url, headers=headers, cookies=cookies, timeout=30)
        content_type = r.headers.get("Content-Type", "")

        if r.status_code == 200 and "image" in content_type:
            with open(file_path, "wb") as img:
                img.write(r.content)
            msg = f"[OK] {isbn}"
            print(msg)
            log_lines.append(msg)
            stats["ok"] += 1

        elif r.status_code == 403:
            msg = f"[FAIL] {isbn} Status=403，cf_clearance 可能已失效"
            print(msg)
            log_lines.append(msg)
            stats["fail"] += 1
            break

        else:
            msg = f"[FAIL] {isbn} Status={r.status_code} Type={content_type}"
            print(msg)
            log_lines.append(msg)
            stats["fail"] += 1

    except Exception as e:
        msg = f"[ERROR] {isbn} {e}"
        print(msg)
        log_lines.append(msg)
        stats["error"] += 1

# ========== 写日志 ==========
summary = (
    f"\n{'=' * 50}\n"
    f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    f"成功: {stats['ok']} | 跳过: {stats['skip']} | 失败: {stats['fail']} | 错误: {stats['error']}\n"
)
print(summary)
log_lines.append(summary)

with open(log_file, "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines))

print(f"[LOG] 日志已保存: {log_file}")
print("[DONE] 全部完成")