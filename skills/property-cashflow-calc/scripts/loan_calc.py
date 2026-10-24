"""貸款（本利平均攤還）與包租回本試算。輸入請用虛構或自己的數字。

  python loan_calc.py pmt  --principal 1000000 --rate 2.0 --months 240
  python loan_calc.py nper --principal 1000000 --rate 2.0 --payment 6000
  python loan_calc.py payback --sunk 120000 --monthly-net 8000
鐵則：反推期數用 NPER（含利息），不要用「餘額 ÷ 月付」。
"""
import argparse
import math


def pmt(principal, annual_rate_pct, months):
    r = annual_rate_pct / 100 / 12
    if months <= 0:
        raise ValueError("期數必須大於 0")
    if r == 0:
        return principal / months
    return principal * r / (1 - (1 + r) ** -months)


def nper(principal, annual_rate_pct, payment):
    r = annual_rate_pct / 100 / 12
    if payment <= 0:
        raise ValueError("月付必須大於 0")
    if r == 0:
        return principal / payment
    if payment <= principal * r:
        raise ValueError("月付不夠支付利息，永遠還不完")
    return -math.log(1 - principal * r / payment) / math.log(1 + r)


def schedule(principal, annual_rate_pct, months):
    """每期：(期別, 月付, 利息, 本金, 期末餘額)。利息 = 當期期初餘額 x 月利率。"""
    r = annual_rate_pct / 100 / 12
    pay = pmt(principal, annual_rate_pct, months)
    bal = principal
    rows = []
    for k in range(1, months + 1):
        interest = bal * r
        prin = pay - interest
        bal -= prin
        rows.append((k, pay, interest, prin, max(bal, 0.0)))
    return rows


def payback_months(sunk_cost, monthly_net):
    """月淨 <= 0 代表不回本，回傳 None。"""
    if monthly_net <= 0:
        return None
    return sunk_cost / monthly_net


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pmt")
    p.add_argument("--principal", type=float, required=True)
    p.add_argument("--rate", type=float, required=True)
    p.add_argument("--months", type=int, required=True)
    n = sub.add_parser("nper")
    n.add_argument("--principal", type=float, required=True)
    n.add_argument("--rate", type=float, required=True)
    n.add_argument("--payment", type=float, required=True)
    b = sub.add_parser("payback")
    b.add_argument("--sunk", type=float, required=True)
    b.add_argument("--monthly-net", type=float, required=True)
    a = ap.parse_args()
    if a.cmd == "pmt":
        print(f"月付：{pmt(a.principal, a.rate, a.months):.2f}")
    elif a.cmd == "nper":
        k = nper(a.principal, a.rate, a.payment)
        print(f"約需 {k:.1f} 期（{k/12:.1f} 年）")
    else:
        m = payback_months(a.sunk, a.monthly_net)
        print("不回本" if m is None else f"回本約 {m:.1f} 個月")


if __name__ == "__main__":
    main()
