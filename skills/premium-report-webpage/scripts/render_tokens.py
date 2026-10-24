"""把 brand.toml 的顏色／字體轉成 CSS tokens，並可套進範本產生示範頁。

  python render_tokens.py --brand ../../../config/brand.example.toml            # 只印 :root CSS
  python render_tokens.py --brand brand.toml --template ../assets/report-template.html --out report.html
"""
import argparse
import tomllib
from pathlib import Path


def css_tokens(brand):
    c, f = brand["colors"], brand["fonts"]
    return (
        ":root{\n"
        f"  --ink:{c['ink']};\n  --paper:{c['paper']};\n  --accent:{c['accent']};\n  --muted:{c['muted']};\n"
        f"  --serif-en:\"{f['serif_en']}\",Georgia,serif;\n"
        f"  --serif-zh:\"{f['serif_zh']}\",\"Songti TC\",serif;\n"
        f"  --fs:{f.get('base_size_rem', 1.0)}rem;\n"
        "}"
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--brand", required=True)
    ap.add_argument("--template")
    ap.add_argument("--out")
    a = ap.parse_args()
    brand = tomllib.loads(Path(a.brand).read_text(encoding="utf-8"))
    css = css_tokens(brand)
    if not a.template:
        print(css)
        return
    tpl = Path(a.template).read_text(encoding="utf-8")
    out = (tpl.replace("/*{{TOKENS}}*/", css)
              .replace("{{BRAND_NAME}}", brand["brand"]["name"])
              .replace("{{FOOTER}}", brand["brand"]["footer_credit"]))
    Path(a.out).write_text(out, encoding="utf-8")
    print("已輸出", a.out)


if __name__ == "__main__":
    main()
