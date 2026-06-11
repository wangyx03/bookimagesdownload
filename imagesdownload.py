import pandas as pd
import requests
import os

csv_file = "books.csv"
save_dir = "covers"

os.makedirs(save_dir, exist_ok=True)

df = pd.read_csv(csv_file)

for _, row in df.iterrows():
    isbn = str(row["SKU"]).strip()
    url = str(row["ImageURL"]).strip()

    try:
        r = requests.get(
            url,
            timeout=20,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        if r.status_code == 200 and "image" in r.headers.get("Content-Type", ""):
            with open(f"{save_dir}/{isbn}.jpg", "wb") as f:
                f.write(r.content)
            print(f"OK {isbn}")
        else:
            print(f"FAIL {isbn} {r.status_code}")

    except Exception as e:
        print(f"ERROR {isbn}: {e}")