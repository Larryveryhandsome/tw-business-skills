"""解析 LINE 群組匯出 txt（tab 分隔），輸出筆數核對與匿名化統計。

  python parse_line_export.py chat.txt [--json out.json]
格式假設（各版 LINE 略有差異，解析後務必核對筆數）：
  日期行：2026.01.05 星期一  或  2026/01/05(一)
  訊息行：14:30<TAB>名稱<TAB>內容   （上午/下午 12 小時制也支援）
  續行：不符合上述格式者接到上一則訊息
發言者一律改成「成員A、成員B…」，輸出不含真名。
"""
import argparse
import json
import re
import sys
from collections import Counter

DATE_RE = re.compile(r"^(\d{4})[./-](\d{1,2})[./-](\d{1,2})")
MSG_RE = re.compile(r"^(上午|下午)?\s*(\d{1,2}):(\d{2})\t([^\t]*)\t(.*)$")


def label(i):
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return f"成員{s}"


def parse(text):
    msgs, date, aliases = [], None, {}
    pattern_lines = 0
    for line in text.splitlines():
        m = MSG_RE.match(line)
        if m and date:
            ap, hh, mm, name, body = m.groups()
            hh = int(hh)
            if ap == "下午" and hh < 12:
                hh += 12
            if ap == "上午" and hh == 12:
                hh = 0
            alias = aliases.setdefault(name, label(len(aliases)))
            msgs.append({"date": date, "time": f"{hh:02d}:{mm}", "who": alias, "text": body})
            pattern_lines += 1
            continue
        d = DATE_RE.match(line)
        if d:
            date = "%s-%02d-%02d" % (d.group(1), int(d.group(2)), int(d.group(3)))
            continue
        if msgs and line.strip():
            msgs[-1]["text"] += "\n" + line
    return msgs, pattern_lines


def summarize(msgs):
    by_who = Counter(m["who"] for m in msgs)
    by_day = Counter(m["date"] for m in msgs)
    total = len(msgs)
    return {
        "total": total,
        "by_member": {k: {"count": v, "share": round(v / total, 3)} for k, v in by_who.most_common()} if total else {},
        "peak_day": by_day.most_common(1)[0] if by_day else None,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--json")
    a = ap.parse_args()
    text = open(a.file, encoding="utf-8-sig").read()
    msgs, pattern_lines = parse(text)
    if len(msgs) != pattern_lines:
        print("筆數核對失敗，請勿交件", file=sys.stderr)
        sys.exit(1)
    s = summarize(msgs)
    print(f"解析 {s['total']} 則訊息；符合訊息格式的行數 {pattern_lines}（相同＝核對通過）")
    for k, v in s["by_member"].items():
        print(f"  {k}: {v['count']} 則（{v['share']:.1%}）")
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump({"summary": s, "messages": msgs}, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
