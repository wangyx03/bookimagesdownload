"""
文件名清单工具（图形界面）

选择一个文件夹，把里面所有文件名导出为 CSV。
列: filename, isbn, size_bytes, modified, (subfolder)

运行:
    py -3.13 list_files_gui.py
"""
import csv
import os
import re
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

ISBN_RE = re.compile(r"97[89]\d{10}")


# ========== 核心逻辑 ==========
def collect_files(folder: Path, recursive: bool, ext_filter: str):
    """返回文件列表；ext_filter 如 '.jpg,.png'，留空表示全部"""
    exts = {
        ("." + e.strip().lstrip(".")).lower()
        for e in ext_filter.split(",")
        if e.strip()
    }
    pattern = folder.rglob("*") if recursive else folder.iterdir()
    files = [
        p for p in pattern
        if p.is_file() and (not exts or p.suffix.lower() in exts)
    ]
    return sorted(files, key=lambda p: str(p.relative_to(folder)).lower())


def write_csv(files, folder: Path, out_file: Path, recursive: bool):
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        header = ["filename", "isbn", "size_bytes", "modified"]
        if recursive:
            header.append("subfolder")
        w.writerow(header)
        for p in files:
            st = p.stat()
            m = ISBN_RE.search(p.stem)
            row = [
                p.name,
                m.group(0) if m else "",
                st.st_size,
                datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            ]
            if recursive:
                sub = p.parent.relative_to(folder)
                row.append("" if str(sub) == "." else str(sub))
            w.writerow(row)


# ========== 界面 ==========
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("文件名清单工具")
        self.geometry("680x330")
        self.minsize(560, 300)

        default_in = os.getenv("SAVE_DIR", "")
        default_out_dir = os.getenv("LOG_DIR") or default_in or str(Path.home())

        self.in_var = tk.StringVar(value=default_in)
        self.out_var = tk.StringVar(value=self._default_out(default_out_dir))
        self.ext_var = tk.StringVar(value="")
        self.rec_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="选择文件夹后点击「导出清单」")

        pad = {"padx": 10, "pady": 6}
        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=8, pady=8)
        frm.columnconfigure(1, weight=1)

        ttk.Label(frm, text="输入文件夹:").grid(row=0, column=0, sticky="w", **pad)
        ttk.Entry(frm, textvariable=self.in_var).grid(row=0, column=1, sticky="ew", **pad)
        ttk.Button(frm, text="浏览…", command=self.pick_input).grid(row=0, column=2, **pad)

        ttk.Label(frm, text="输出文件:").grid(row=1, column=0, sticky="w", **pad)
        ttk.Entry(frm, textvariable=self.out_var).grid(row=1, column=1, sticky="ew", **pad)
        ttk.Button(frm, text="浏览…", command=self.pick_output).grid(row=1, column=2, **pad)

        ttk.Label(frm, text="文件类型:").grid(row=2, column=0, sticky="w", **pad)
        ttk.Entry(frm, textvariable=self.ext_var).grid(row=2, column=1, sticky="ew", **pad)
        ttk.Label(frm, text="如 .jpg,.png；留空=全部", foreground="gray").grid(
            row=2, column=2, sticky="w", **pad
        )

        ttk.Checkbutton(frm, text="包含子文件夹", variable=self.rec_var).grid(
            row=3, column=1, sticky="w", **pad
        )

        btns = ttk.Frame(frm)
        btns.grid(row=4, column=0, columnspan=3, pady=12)
        ttk.Button(btns, text="导出清单", command=self.run).pack(side="left", padx=6)
        self.open_btn = ttk.Button(btns, text="打开输出文件", command=self.open_output, state="disabled")
        self.open_btn.pack(side="left", padx=6)
        ttk.Button(btns, text="打开所在文件夹", command=self.open_output_dir).pack(side="left", padx=6)

        ttk.Label(frm, textvariable=self.status_var, wraplength=620, justify="left").grid(
            row=5, column=0, columnspan=3, sticky="w", **pad
        )

    @staticmethod
    def _default_out(folder):
        return str(Path(folder) / f"file_list_{datetime.now():%Y%m%d_%H%M%S}.csv")

    def pick_input(self):
        d = filedialog.askdirectory(
            title="选择输入文件夹", initialdir=self.in_var.get() or str(Path.home())
        )
        if d:
            self.in_var.set(str(Path(d)))

    def pick_output(self):
        cur = Path(self.out_var.get()) if self.out_var.get() else None
        f = filedialog.asksaveasfilename(
            title="选择输出文件",
            defaultextension=".csv",
            filetypes=[("CSV 文件", "*.csv")],
            initialdir=str(cur.parent) if cur else str(Path.home()),
            initialfile=cur.name if cur else "file_list.csv",
        )
        if f:
            self.out_var.set(str(Path(f)))

    def run(self):
        folder = Path(self.in_var.get().strip().strip('"'))
        out_text = self.out_var.get().strip().strip('"')

        if not folder.is_dir():
            messagebox.showerror("错误", f"输入文件夹不存在:\n{folder}")
            return
        if not out_text:
            messagebox.showerror("错误", "请选择输出文件")
            return

        out_file = Path(out_text)
        if out_file.suffix.lower() != ".csv":
            out_file = out_file.with_suffix(".csv")
        if out_file.exists() and not messagebox.askyesno("确认", f"文件已存在，是否覆盖？\n{out_file}"):
            return

        self.status_var.set("正在读取…")
        self.update_idletasks()
        try:
            files = collect_files(folder, self.rec_var.get(), self.ext_var.get())
            write_csv(files, folder, out_file, self.rec_var.get())
        except PermissionError:
            messagebox.showerror("错误", f"无法写入，文件可能正在 Excel 中打开:\n{out_file}")
            self.status_var.set("导出失败")
            return
        except Exception as e:
            messagebox.showerror("错误", str(e))
            self.status_var.set("导出失败")
            return

        self.last_output = out_file
        self.open_btn.config(state="normal")
        self.status_var.set(f"完成：共 {len(files)} 个文件\n已保存到 {out_file}")
        # 下次导出默认用新文件名，避免覆盖
        self.out_var.set(self._default_out(out_file.parent))

    def open_output(self):
        f = getattr(self, "last_output", None)
        if f and f.exists():
            os.startfile(f)

    def open_output_dir(self):
        d = Path(self.out_var.get()).parent
        if d.is_dir():
            os.startfile(d)
        else:
            messagebox.showinfo("提示", f"文件夹不存在:\n{d}")


if __name__ == "__main__":
    App().mainloop()
