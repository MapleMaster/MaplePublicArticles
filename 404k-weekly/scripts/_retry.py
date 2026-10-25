import json, sys, time, logging
sys.stdout.reconfigure(encoding="utf-8")
logging.getLogger("futu").setLevel(logging.WARNING)
from futu import OpenQuoteContext, KLType, AuType
P = r"F:\Projects\AI\MaplePublicArticles\404k-weekly\scripts\_px_1025.json"
out = json.load(open(P, encoding="utf-8"))
todo = {"US.NVDA":"英伟达","US.WDC":"西部数据","US.STX":"希捷","US.CRVW":"CoreWeave","US.LRCX":"泛林","US.AMAT":"应用材料"}
q = OpenQuoteContext(host="127.0.0.1", port=11111)
for code,name in todo.items():
    for a in range(3):
        time.sleep(6)
        r = q.request_history_kline(code, start="2026-10-08", end="2026-10-25", ktype=KLType.K_DAY, autype=AuType.QFQ, max_count=30)
        if r[0]==0:
            out[code]={"name":name,"bars":[{"d":str(t)[:10],"c":float(c)} for t,c in zip(r[1]["time_key"],r[1]["close"])]}
            print("OK",code,len(r[1]),flush=True); break
        print("ERR",code,r[1],flush=True)
q.close()
json.dump(out, open(P,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("TOTAL",len(out),flush=True)
