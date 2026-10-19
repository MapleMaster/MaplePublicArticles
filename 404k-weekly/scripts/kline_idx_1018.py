# -*- coding: utf-8 -*-
import json, sys, time, logging
sys.stdout.reconfigure(encoding="utf-8")
logging.getLogger("futu").setLevel(logging.WARNING)
from futu import OpenQuoteContext, KLType, AuType

MORE = {
    "SH.000001": "上证综指", "SZ.399001": "深证成指", "SZ.399006": "创业板指",
    "SH.000688": "科创50", "SH.000300": "沪深300",
    "HK.800000": "恒生指数", "HK.800700": "恒生科技",
    "US.IXIC": "纳斯达克", "US.DJI": "道琼斯", "US.SPX": "标普500", "US.SOX": "费城半导体",
    "US.NVDA": "英伟达", "US.CRWV": "CoreWeave", "US.STX": "希捷",
    "US.AMD": "AMD", "US.MSFT": "微软", "US.GOOGL": "谷歌", "US.AMZN": "亚马逊", "US.META": "Meta",
    "US.LITE": "Lumentum", "US.AAOI": "应用光电", "US.ANET": "Arista", "US.KLAC": "科磊",
    "US.VRT": "Vertiv", "US.CREDO": "Credo",
}
out = {}
q = OpenQuoteContext(host="127.0.0.1", port=11111)
for code, name in MORE.items():
    r = q.request_history_kline(code, start="2026-10-01", end="2026-10-18", ktype=KLType.K_DAY,
                                autype=AuType.QFQ, max_count=30)
    if r[0] == 0:
        out[code] = {"name": name, "bars": [
            {"d": str(row["time_key"])[:10], "c": float(row["close"])} for _, row in r[1].iterrows()]}
        print("OK", code, name, len(r[1]))
    else:
        print("ERR", code, name, str(r[1])[:80])
    time.sleep(0.25)
q.close()
json.dump(out, open(r"F:\Projects\AI\MaplePublicArticles\404k-weekly\scripts\_px_idx_1018.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("DONE", len(out))
