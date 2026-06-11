import sys
sys.stdout.reconfigure(encoding="utf-8")

import csv
import re
import requests
from pathlib import Path
from dotenv import load_dotenv
import os

# ========== 读取 .env ==========
load_dotenv()

CF_CLEARANCE = os.getenv("CF_CLEARANCE")

if not CF_CLEARANCE:
    raise ValueError("CF_CLEARANCE 未配置，请检查 .env 文件")

# ========== 配置 ==========
csv_file_path = r"D:\book images\bookimages.csv"
save_dir = Path(r"D:\book images\covers")
save_dir.mkdir(parents=True, exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    "Referer": "https://images.bookdepot.com/",
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
}

cookies = {
    "cf_clearance": CF_CLEARANCE
}

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

        if url.lower() == "image":
            continue

        urls.append(url)

print(f"[OK] 共读取 {len(urls)} 个URL")

# ========== 下载 ==========
session = requests.Session()

for url in urls:
    url = "https://" + url if not url.startswith("http") else url
    isbn = extract_isbn(url)

    if not isbn:
        print("[SKIP] 无法提取ISBN:", url)
        continue

    file_path = save_dir / f"{isbn}.jpg"

    # 避免重复下载；小于5KB认为可能是坏文件，重新下载
    if file_path.exists() and file_path.stat().st_size > 5000:
        print("[SKIP] 已存在:", isbn)
        continue

    try:
        r = session.get(
            url,
            headers=headers,
            cookies=cookies,
            timeout=30
        )

        content_type = r.headers.get("Content-Type", "")

        if r.status_code == 200 and "image" in content_type:
            with open(file_path, "wb") as img:
                img.write(r.content)

            print("[OK]", isbn)

        elif r.status_code == 403:
            print("[FAIL]", isbn, "Status=403，cf_clearance 可能已失效，请更新 .env")
            break

        else:
            print("[FAIL]", isbn, "Status=", r.status_code, "Type=", content_type)

    except Exception as e:
        print("[ERROR]", isbn, e)

print("[DONE] 全部完成")