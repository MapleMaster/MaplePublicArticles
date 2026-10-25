# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
d = json.load(open(r"_px_1025.json", encoding="utf-8"))
def get(code, date):
    b = {x["d"]: x["c"] for x in d[code]["bars"]}
    return b.get(date)
print(f"{'代码':<12}{'名称':<14}{'10/16':>10}{'10/23':>10}{'周涨跌':>9}   {'周内最低':>9}")
for code, v in d.items():
    a = get(code, "2026-10-16"); b = get(code, "2026-10-23")
    if a is None or b is None:
        bars = [x for x in v["bars"] if "2026-10-19" <= x["d"] <= "2026-10-23"]
        print(f"{code:<12}{v['name']:<14}{'NA':>10}{(bars[-1]['c'] if bars else 0):>10.3f}   (缺10/16或10/23)")
        continue
    lows = [x["l"] for x in v["bars"] if "2026-10-19" <= x["d"] <= "2026-10-23"]
    print(f"{code:<12}{v['name']:<14}{a:>10.3f}{b:>10.3f}{(b/a-1)*100:>8.2f}%   {min(lows) if lows else 0:>9.3f}")
