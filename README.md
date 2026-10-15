# Book Cover Bulk Downloader — Usage Guide

Downloads covers using your **everyday Chrome**, which avoids Python being blocked by Cloudflare.
Python only builds the download list; the browser does the actual downloading and writes images straight into the `covers` folder.

---

## 1. One-time setup (already done — reference for a new machine)

`.env` (in `D:\Git\bookimagesdownload`):

```dotenv
SITE=bookdepot
CSV_FILE=H:\My Drive\Bomie\OMS Management\OMS Pictures\Bookcover\bookimages.csv
SAVE_DIR=H:\My Drive\Bomie\OMS Management\OMS Pictures\Bookcover\covers
LOG_DIR=H:\My Drive\Bomie\OMS Management\OMS Pictures\Bookcover
```

`.gitignore` should include:

```
.env
chrome_profile/
console_download.js
```

Dependency: `py -3.13 -m pip install python-dotenv`

---

## 2. Steps for each download run

### Step 1 — Update the CSV
Put the new image links into `bookimages.csv` (image URL in the first column; Markdown links are supported).

### Step 2 — Generate the download script
```powershell
cd D:\Git\bookimagesdownload
py -3.13 make_console_js.py
```
Output looks like `[OK] 待下载: 146 | 已存在跳过: 70` (to download / already present, skipped) and creates `console_download.js`.

### Step 3 — Open a cover in Chrome and pass verification
In your **everyday Chrome** (not an automation-launched window), open any cover, e.g.:
```
https://images.bookdepot.com/covers/large/isbn978006/9780063205031-l.jpg
```
- If "Verify you are human" appears, click it and wait until the **image is displayed**.
- Make sure DevTools device emulation is off: press **Ctrl+Shift+M**; "Dimensions: Responsive" should not appear at the top.

### Step 4 — Quick test (optional but recommended)
F12 → **Console**, run:
```js
fetch(location.href).then(r => console.log(r.status, r.headers.get("content-type")))
```
- `200 image/jpeg` → continue.
- `403` → see Troubleshooting.

### Step 5 — Run the download script
1. Open `console_download.js` in VS Code, **Ctrl+A → Ctrl+C**.
2. Paste into the Chrome Console and press Enter.
   If Chrome blocks pasting the first time, type `allow pasting`, press Enter, then paste again.
3. When the folder picker opens, paste this path into the **Folder:** box at the bottom and press Enter:
   ```
   H:\My Drive\Bomie\OMS Management\OMS Pictures\Bookcover\covers
   ```
4. When Chrome asks for permission, choose **Allow / Edit files**.

### Step 6 — Check the results
The Console prints `[n/total] OK ISBN size` per image, about one per second.
At the end it shows `DONE 成功=… 已存在跳过=… 失败=…` (succeeded / skipped / failed) plus a list of failed ISBNs.

---

## 3. Resuming after an interruption

Refresh the page → pass verification → paste the **same** `console_download.js` again.
The script checks the `covers` folder and skips anything already downloaded.
(If the CSV changed, re-run Step 2 first.)

---

## 4. Troubleshooting

| Symptom | Cause / Fix |
|---|---|
| Page keeps asking for verification in a loop | You're in an automation-controlled browser. Use your everyday Chrome. |
| Image shows on the page, but the script gets 403 on the first one | DevTools device emulation or a UA override is on. Press Ctrl+Shift+M; in Network conditions set User agent to "Use browser default"; close DevTools, refresh, and verify again. |
| Log shows `保存到文件夹: New folder` (or another wrong name) | Wrong folder selected. Run again and choose `covers`. |
| Mouse cursor disappears in the folder picker | Paste the path into the Folder: box and press Enter, or press Alt+Tab to switch windows and back. |
| Chrome won't allow selecting a folder on H: | Click Cancel in the picker; the script falls back to the Downloads folder. Move the files to `covers` afterwards. |
| `连续失败 10 次，停止` (stopped after 10 consecutive failures) | Check the status codes in the Console; usually you need to re-verify, or the site is rate-limiting — wait a bit and retry. |
| `待下载: 0` (nothing to download) | All covers already exist, or the CSV links don't match the `SITE` domain. |

---

## 5. Switching sites (bookoutlet)

1. Set `SITE=bookoutlet` in `.env`.
2. Re-run `make_console_js.py`.
3. In Step 3, open a **bookoutlet cover image** in Chrome and run the script in that page's Console.
   (The script must run on a page with the same domain as the images.)

---

## 6. Files

| File | Purpose |
|---|---|
| `make_console_js.py` | **Current method**: reads the CSV, skips existing covers, generates `console_download.js` |
| `console_download.js` | Generated browser script — regenerate before each run |
| `imagesdownload.py` | Old method (curl_cffi + copied cookie); mostly broken by Cloudflare, kept for reference |
| `chrome_profile/` | Leftover from the Playwright attempt; safe to delete |
