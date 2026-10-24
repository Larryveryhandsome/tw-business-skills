"""薪資換算與加班費試算（輔助檢核用，非法律意見）。

用法：
  python wage_calc.py --monthly 30000 --weekday-ot 3
  python wage_calc.py --monthly 30000 --restday-hours 6

倍率（平日 1.34／1.67、休息日 1.34／1.67／2.67、休息日 4/8/12 計算單位）
是常見的實務計法，使用前請對照《勞動基準法》§24 與主管機關最新解釋。
金額四捨五入到元。月薪換算：日薪 = 月薪/30、時薪 = 月薪/240。
"""
import argparse


def hourly(monthly):
    return monthly / 240


def daily(monthly):
    return monthly / 30


def weekday_overtime_pay(monthly, ot_hours):
    """平日延長工時加班費：時薪 x 倍率 x 時數。前 2 小時 x1.34，其後 x1.67（本函式最多算到 4 小時）。"""
    if ot_hours < 0:
        raise ValueError("時數不可為負")
    if ot_hours > 4:
        raise ValueError("平日延長工時合計上限另受 §32 限制，本函式只算到 4 小時")
    h = hourly(monthly)
    first = min(ot_hours, 2)
    rest = max(ot_hours - 2, 0)
    return round(h * (first * 1.34 + rest * 1.67))


def restday_counted_hours(worked):
    """休息日出勤的計算單位：4 / 8 / 12 小時。"""
    if worked <= 0:
        return 0
    if worked > 12:
        raise ValueError("休息日出勤超過 12 小時，請另行處理")
    return 4 if worked <= 4 else 8 if worked <= 8 else 12


def restday_pay(monthly, worked_hours):
    n = restday_counted_hours(worked_hours)
    h = hourly(monthly)
    total = 0.0
    for i in range(1, n + 1):
        mult = 1.34 if i <= 2 else 1.67 if i <= 8 else 2.67
        total += h * mult
    return round(total)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--monthly", type=float, required=True, help="月薪（元）")
    ap.add_argument("--weekday-ot", type=float, default=0, help="平日延長工時（小時）")
    ap.add_argument("--restday-hours", type=float, default=0, help="休息日實際出勤（小時）")
    a = ap.parse_args()
    print(f"日薪（月薪/30）：{daily(a.monthly):.1f}")
    print(f"時薪（月薪/240）：{hourly(a.monthly):.2f}")
    if a.weekday_ot:
        print(f"平日加班 {a.weekday_ot} 小時：{weekday_overtime_pay(a.monthly, a.weekday_ot)} 元")
    if a.restday_hours:
        print(f"休息日出勤 {a.restday_hours} 小時（計 {restday_counted_hours(a.restday_hours)} 小時單位）：{restday_pay(a.monthly, a.restday_hours)} 元")
    print("以上為試算，非法律意見；請以現行法規與主管機關公告為準。")


if __name__ == "__main__":
    main()
