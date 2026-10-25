import json, sys, time, logging
sys.stdout.reconfigure(encoding="utf-8")
logging.getLogger("futu").setLevel(logging.WARNING)
from futu import OpenQuoteContext, KLType, AuType
P = r"_px_1025.json"
out = json.load(open(P, encoding="utf-8"))
todo = {"HK.06166":"剑桥科技"}
q = OpenQuoteContext(host="127.0.0.1", port=11111)
for code,name in todo.items():
    time.sleep(3)
    r = q.request_history_kline(code, start="2026-10-08", end="2026-10-25", ktype=KLType.K_DAY, autype=AuType.QFQ, max_count=30)
    if r[0]==0:
        out[code]={"name":name,"bars":[{"d":str(t)[:10],"c":float(c),"l":float(l)} for t,c,l in zip(r[1]["time_key"],r[1]["close"],r[1]["low"])]}
        for row in r[1].itertuples(index=False):
            print(str(row.time_key)[:10], float(row.close))
    else:
        print("ERR", r[1])
q.close()
json.dump(out, open(P,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
for c in ["US.NVDA","US.WDC","US.STX","US.LRCX","US.AMAT"]:
    print(c, [(b["d"][5:], b["c"]) for b in out[c]["bars"] if b["d"]>="2026-10-15"])
