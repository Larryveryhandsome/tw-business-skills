"""tw-business-skills 測試：SKILL.md frontmatter、腳本邏輯、示範輸出。
執行：python -X utf8 -m unittest discover -s tests -v
"""
import importlib.util
import os
import re
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
EXPECTED = {
    "tw-labor-compliance-check", "tw-legal-redflag-check", "premium-report-webpage", "client-brand-site-builder",
    "chat-meeting-digest", "property-cashflow-calc", "brokerage-forms-a4", "venture-falsify-kpi",
}


def load(rel):
    p = SKILLS / rel
    spec = importlib.util.spec_from_file_location(p.stem, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class FrontmatterTest(unittest.TestCase):
    def test_all_skills_present_and_valid(self):
        self.assertEqual({p.name for p in SKILLS.iterdir() if p.is_dir()}, EXPECTED)
        for name in EXPECTED:
            text = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
            m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
            self.assertIsNotNone(m, name)
            fm = m.group(1)
            self.assertRegex(fm, rf"(?m)^name: {re.escape(name)}$")
            self.assertRegex(fm, r"(?m)^description:")
            self.assertGreater(len(fm), 120, name)

    def test_legal_skills_have_disclaimer(self):
        for name in ("tw-labor-compliance-check", "tw-legal-redflag-check"):
            t = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("非法律意見", t)
            self.assertIn("原則上", t)


class WageTest(unittest.TestCase):
    def setUp(self):
        self.m = load("tw-labor-compliance-check/scripts/wage_calc.py")

    def test_rates(self):
        self.assertEqual(self.m.hourly(24000), 100)
        self.assertEqual(self.m.daily(30000), 1000)

    def test_weekday(self):
        self.assertEqual(self.m.weekday_overtime_pay(24000, 2), 268)   # 100*2*1.34
        self.assertEqual(self.m.weekday_overtime_pay(24000, 3), 435)   # 268 + 167
        with self.assertRaises(ValueError):
            self.m.weekday_overtime_pay(24000, 5)

    def test_restday_units(self):
        self.assertEqual(self.m.restday_counted_hours(1), 4)
        self.assertEqual(self.m.restday_counted_hours(5), 8)
        self.assertEqual(self.m.restday_counted_hours(9), 12)
        # 4 小時單位：2*1.34 + 2*1.67 = 6.02 -> 602
        self.assertEqual(self.m.restday_pay(24000, 3), 602)


class LoanTest(unittest.TestCase):
    def setUp(self):
        self.m = load("property-cashflow-calc/scripts/loan_calc.py")

    def test_pmt_known_value(self):
        self.assertAlmostEqual(self.m.pmt(1_000_000, 2.0, 240), 5058.83, delta=0.01)
        self.assertAlmostEqual(self.m.pmt(120000, 0, 12), 10000)

    def test_nper_roundtrip(self):
        pay = self.m.pmt(1_000_000, 2.0, 240)
        self.assertAlmostEqual(self.m.nper(1_000_000, 2.0, pay), 240, places=4)
        # 不能用 餘額/月付 代替
        self.assertNotAlmostEqual(1_000_000 / pay, 240, places=0)

    def test_schedule_ends_at_zero(self):
        rows = self.m.schedule(500000, 3.0, 60)
        self.assertAlmostEqual(rows[-1][4], 0, delta=0.01)
        self.assertGreater(rows[0][2], rows[-1][2])  # 利息遞減

    def test_payback(self):
        self.assertEqual(self.m.payback_months(120000, 8000), 15)
        self.assertIsNone(self.m.payback_months(1000, 0))
        with self.assertRaises(ValueError):
            self.m.nper(1_000_000, 2.0, 1000)


class LineParseTest(unittest.TestCase):
    def test_sample(self):
        m = load("chat-meeting-digest/scripts/parse_line_export.py")
        text = (SKILLS / "chat-meeting-digest/samples/synthetic_line.txt").read_text(encoding="utf-8")
        msgs, n = m.parse(text)
        self.assertEqual(len(msgs), n)
        self.assertEqual(len(msgs), 4)
        self.assertEqual(msgs[2]["time"], "13:10")
        self.assertIn("這是續行", msgs[2]["text"])
        self.assertEqual({x["who"] for x in msgs}, {"成員A", "成員B"})
        self.assertNotIn("王小明", str(msgs))


class ReceiptTest(unittest.TestCase):
    def setUp(self):
        self.m = load("brokerage-forms-a4/scripts/make_receipt.py")

    def test_upper_amount(self):
        f = self.m.to_upper_amount
        self.assertEqual(f(100000), "壹拾萬元整")
        self.assertEqual(f(1234567), "壹佰貳拾參萬肆仟伍佰陸拾柒元整")
        self.assertEqual(f(1000500), "壹佰萬零伍佰元整")
        self.assertEqual(f(10005000), "壹仟萬零伍仟元整")
        self.assertEqual(f(100010000), "壹億零壹萬元整")
        self.assertEqual(f(0), "零元整")

    def test_html_and_pdf_one_page(self):
        brand = tomllib.loads((ROOT / "config/brand.example.toml").read_text(encoding="utf-8"))
        data = tomllib.loads((SKILLS / "brokerage-forms-a4/scripts/receipt.example.toml").read_text(encoding="utf-8"))
        html = self.m.build_html(brand, data)
        self.assertIn("壹拾萬元整", html)
        self.assertIn("自願選擇斡旋金", html)
        self.assertIn("本文件為範本", html)
        if os.environ.get("RUN_PDF_TEST") and self.m.find_browser():
            with tempfile.TemporaryDirectory() as d:
                h = Path(d) / "r.html"
                h.write_text(html, encoding="utf-8")
                self.assertEqual(self.m.to_pdf(h, Path(d) / "r.pdf"), 1)


class TokensTest(unittest.TestCase):
    def test_render(self):
        m = load("premium-report-webpage/scripts/render_tokens.py")
        brand = tomllib.loads((ROOT / "config/brand.example.toml").read_text(encoding="utf-8"))
        css = m.css_tokens(brand)
        self.assertIn(brand["colors"]["ink"], css)
        r = subprocess.run([sys.executable, "-X", "utf8", str(SKILLS / "premium-report-webpage/scripts/render_tokens.py"),
                            "--brand", str(ROOT / "config/brand.example.toml"),
                            "--template", str(SKILLS / "premium-report-webpage/assets/report-template.html"),
                            "--out", str(Path(tempfile.gettempdir()) / "tw_bs_report_test.html")],
                           capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stderr)
        out = (Path(tempfile.gettempdir()) / "tw_bs_report_test.html").read_text(encoding="utf-8")
        self.assertNotIn("{{", out)
        self.assertIn("--ink:" + brand["colors"]["ink"], out)


if __name__ == "__main__":
    unittest.main()
