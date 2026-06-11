import sys
sys.stdout.reconfigure(encoding="utf-8")

import csv
import re
import os
import requests
from pathlib import Path

csv_file_path = r"D:\book images\bookimages.csv"
save_dir = Path(r"D:\book images\covers")
save_dir.mkdir(parents=True, exist_ok=True)

cf_clearance = "fO0EBOps1ApHbOTO.vAtmZqgDNlx6DXsrXXpCroCzeU-1781200295-1.2.1.1-jCuJ_.06F1rpreWO1vz3uG8OpGCCUs1Bk4YrSNtnJ_0Z7zjvzgrDJN5AL0KtwosjRnYN8xS70MUmwhZ.vDglRDtvLidV4WXzC7MEogWF3VMilGkRIKAeVVo_iFdmhfoYhQA_9UGMfton_T2TrzhqdGL3DgWdAxjpWu23RoeThIJ3gRKI0JnRL0wsfr659avZdp1ZaPawabSu2GxvMxNaWBQpPzwTfRTE9IHC1580B78o_Oc96TRtI54OAESfIcDN_OnCdL.MvM9pSU4vvSUoKzm8wZ2E02xAXi5t1vTnMz6M1aLVEBZ6Umarj_t3dYIKFW7baPjrGcv0ZwQgrhbx818GPJUmGykYsjOOg8iyWyDPW7q5kDRxL1Sk2KgmpACd.Ym_8F7DvywsFTjndKefv.bqFaBSN71xUcANq6lOTgI"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    "Referer": "https://images.bookdepot.com/",
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
}

cookies = {
    "cf_clearance": cf_clearance
}

def extract_isbn(url):
    m = re.search(r"/(97[89]\d{10})-l\.jpg", url)
    if m:
        return m.group(1)
    m = re.search(r"(97[89]\d{10})", url)
    if m:
        return m.group(1)
    return None

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

session = requests.Session()

for url in urls:
    url = "https://" + url if not url.startswith("http") else url
    isbn = extract_isbn(url)

    if not isbn:
        print("[SKIP] 无法提取ISBN:", url)
        continue

    file_path = save_dir / f"{isbn}.jpg"

    if file_path.exists():
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

        else:
            print("[FAIL]", isbn, "Status=", r.status_code, "Type=", content_type)

    except Exception as e:
        print("[ERROR]", isbn, e)

print("[DONE] 全部完成")