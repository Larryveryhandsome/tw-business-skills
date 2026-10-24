"""斡旋金簽收單（A4 單頁）產生器：抬頭取自 brand.toml，案件資料取自 receipt.toml。

  python make_receipt.py --brand ../../../config/brand.example.toml --data receipt.example.toml --out out.html [--pdf out.pdf]

--pdf 需要本機有 Chrome / Edge（可用環境變數 CHROME_PATH 指定），以 headless 列印並驗證頁數必須是 1。
本文件為範本，正式簽署前請送法務或代書審閱。
"""
import argparse
import html
import os
import re
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

DIGITS = "零壹貳參肆伍陸柒捌玖"
UNITS = ["", "拾", "佰", "仟"]


def _section(n):
    """0 < n < 10000 的大寫（含內部的零）。"""
    out, pending = "", False
    for pos in (3, 2, 1, 0):
        d = (n // 10 ** pos) % 10
        if d == 0:
            if out:
                pending = True
            continue
        if pending:
            out += "零"
            pending = False
        out += DIGITS[d] + UNITS[pos]
    return out


def to_upper_amount(n):
    """整數金額轉國字大寫，例：1234567 -> 壹佰貳拾參萬肆仟伍佰陸拾柒元整。"""
    if not isinstance(n, int) or n < 0:
        raise ValueError("金額必須是非負整數")
    if n == 0:
        return "零元整"
    if n >= 10 ** 12:
        raise ValueError("金額過大")
    groups = [(n // 10 ** 8 % 10000, "億"), (n // 10 ** 4 % 10000, "萬"), (n % 10000, "")]
    out, prev, skipped = "", 0, False
    for g, u in groups:
        if g == 0:
            skipped = True
            continue
        s = _section(g)
        if out and (skipped or g < 1000 or prev % 10 == 0):
            out += "零"
        out += s + u
        prev, skipped = g, False
    return out + "元整"


def build_html(brand, data):
    h = brand["letterhead"]
    e = html.escape
    rows = "".join(
        f"<tr><td>{e(p['parcel'])}</td><td>{e(str(p['area']))}</td></tr>" for p in data["parcels"]
    )
    amount = int(data["amount"])
    acc = brand["colors"]["accent"]
    return f"""<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">
<title>斡旋金簽收單</title>
<style>
@page {{ size: A4; margin: 12mm; }}
body {{ font-family: "Noto Serif CJK TC","Noto Serif TC","Microsoft JhengHei",serif; font-size: 10.5pt; line-height: 1.6; color:#111; }}
h1 {{ text-align:center; font-size: 16pt; margin: 0 0 4mm; border-bottom: 1px solid {acc}; padding-bottom: 2mm; }}
.meta {{ text-align:center; font-size: 9pt; color:#555; margin-bottom: 4mm; }}
table {{ width:100%; border-collapse: collapse; margin: 3mm 0; }}
td, th {{ border: 1px solid #888; padding: 1.5mm 2mm; }}
.notice {{ border: 1px solid #888; padding: 2mm 3mm; margin: 3mm 0; }}
.sign {{ display:flex; gap: 8mm; margin-top: 8mm; }}
.sign div {{ flex:1; border-top: 1px solid #111; padding-top: 2mm; min-height: 24mm; }}
.foot {{ margin-top: 6mm; font-size: 8.5pt; color:#555; text-align:center; }}
</style></head><body>
<h1>斡旋金簽收單</h1>
<div class="meta">{e(h['company_name'])}｜統編 {e(h['tax_id'])}｜{e(h['address'])}｜{e(h['phone'])}｜編號 {e(h['form_prefix'])}-{e(data['serial'])}</div>
<p>案名：{e(data['case_name'])}　單價：{e(data['unit_price'])}　日期：{e(data['date'])}</p>
<table><tr><th>地號</th><th>面積</th></tr>{rows}</table>
<table><tr><th>斡旋金額</th><td>新臺幣 {amount:,} 元（{to_upper_amount(amount)}）</td></tr>
<tr><th>斡旋有效期間</th><td>{e(data['valid_from'])} 至 {e(data['valid_to'])}</td></tr></table>
<div class="notice"><b>要約書告知：</b>收受斡旋金前，已以書面告知買方得改用主管機關公告之不動產要約書。
買方已知悉並自願選擇斡旋金。</div>
<div class="sign"><div>買方簽章：</div><div>收受人簽章：</div></div>
<div class="foot">本文件為範本，正式簽署前請送法務或代書審閱。</div>
</body></html>"""


def find_browser():
    cands = [os.environ.get("CHROME_PATH", ""),
             r"C:\Program Files\Google\Chrome\Application\chrome.exe",
             r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
             "/usr/bin/google-chrome", "/usr/bin/chromium"]
    return next((c for c in cands if c and Path(c).exists()), None)


def count_pdf_pages(pdf_path):
    data = Path(pdf_path).read_bytes()
    return len(re.findall(rb"/Type\s*/Page(?![s\w])", data))


def to_pdf(html_path, pdf_path):
    exe = find_browser()
    if not exe:
        raise RuntimeError("找不到 Chrome/Edge，請設定 CHROME_PATH")
    with tempfile.TemporaryDirectory() as prof:
        subprocess.run([exe, "--headless=new", "--disable-gpu", f"--user-data-dir={prof}",
                        "--no-pdf-header-footer", f"--print-to-pdf={pdf_path}",
                        Path(html_path).resolve().as_uri()],
                       check=True, capture_output=True, timeout=120)
    pages = count_pdf_pages(pdf_path)
    if pages != 1:
        raise RuntimeError(f"頁數 {pages}，單頁單據必須是 1 頁")
    return pages


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--brand", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--pdf")
    a = ap.parse_args()
    brand = tomllib.loads(Path(a.brand).read_text(encoding="utf-8"))
    data = tomllib.loads(Path(a.data).read_text(encoding="utf-8"))
    Path(a.out).write_text(build_html(brand, data), encoding="utf-8")
    print("已輸出", a.out)
    if a.pdf:
        print("PDF 頁數：", to_pdf(a.out, a.pdf))


if __name__ == "__main__":
    sys.exit(main())
