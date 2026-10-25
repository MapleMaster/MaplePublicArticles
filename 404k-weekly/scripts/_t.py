import logging, sys
sys.stdout.reconfigure(encoding="utf-8")
logging.getLogger("futu").setLevel(logging.WARNING)
from futu import OpenQuoteContext, KLType, AuType
q = OpenQuoteContext(host="127.0.0.1", port=11111)
print("connected", flush=True)
r = q.request_history_kline("SH.588200", start="2026-10-15", end="2026-10-25", ktype=KLType.K_DAY, autype=AuType.QFQ, max_count=10)
print(r[0], flush=True)
if r[0]==0:
    print(r[1][["time_key","close"]].to_string(), flush=True)
else:
    print(r[1], flush=True)
q.close()
