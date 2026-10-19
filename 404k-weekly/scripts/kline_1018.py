# -*- coding: utf-8 -*-
"""本周(10/12-10/16)持仓与跟踪标的价格序列 —— 富途 OpenAPI 直连"""
import json, sys, time, logging
sys.stdout.reconfigure(encoding="utf-8")
logging.getLogger("futu").setLevel(logging.WARNING)
from futu import OpenQuoteContext, KLType, AuType

CODES = {
    # A股 在持仓
    "SZ.300757": "罗博特科", "SH.688072": "拓荆科技", "SH.588710": "科半导体ETF",
    "SZ.159570": "创新药HK", "SZ.000657": "中钨高新", "SH.688008": "澜起科技",
    "SH.588200": "科创芯片ETF",
    # A股 产业链跟踪 / 本周已清仓
    "SZ.300308": "中际旭创", "SZ.300394": "天孚通信", "SH.600183": "生益科技",
    "SZ.300604": "长川科技", "SH.600176": "中国巨石", "SZ.159516": "半导设备ETF",
    "SZ.002428": "云南锗业", "SH.688825": "长鑫科技", "SH.561980": "半导体设备ETF-561980",
    "SH.515880": "通信ETF", "SZ.300502": "新易盛", "SH.603986": "兆易创新",
    "SZ.002913": "奥士康", "SZ.002463": "沪电股份",
    # 港股
    "HK.06869": "长飞光纤光缆", "HK.01888": "建滔积层板", "HK.00148": "建滔集团",
    "HK.00100": "MINIMAX-W", "HK.01548": "金斯瑞生物科技", "HK.00522": "ASMPT",
    # 美股 在持仓
    "US.MU": "美光", "US.MRVL": "迈威尔", "US.INTC": "英特尔", "US.NBIS": "Nebius",
    "US.LRCX": "泛林", "US.AMAT": "应用材料", "US.TER": "泰瑞达", "US.TSM": "台积电",
    "US.BE": "Bloom Energy", "US.CIEN": "Ciena", "US.CLS": "Celestica",
    "US.AVGO": "博通", "US.COHR": "Coherent", "US.ALAB": "Astera Labs",
    "US.IBKR": "盈透", "US.S": "SentinelOne", "US.ATI": "ATI", "US.BA": "波音",
    "US.VST": "Vistra", "US.AAPL": "苹果", "US.HWM": "Howmet", "US.RKLB": "Rocket Lab",
    "US.JPM": "摩根大通", "US.COST": "好市多", "US.TWST": "Twist Bio",
    "US.IONQ": "IonQ", "US.MSTR": "Strategy",
    # 美股 跟踪
    "US.SKHY": "SK海力士ADR", "US.SNDK": "闪迪", "US.DRAM": "DRAM ETF",
    "US.DISK": "DISK ETF", "US.TQQQ": "TQQQ", "US.NVDA": "英伟达",
    "US.WDC": "西部数据", "US.STX": "希捷", "US.CRWV": "CoreWeave",
}

START, END = "2026-10-01", "2026-10-18"
out = {}
q = OpenQuoteContext(host="127.0.0.1", port=11111)
for code, name in CODES.items():
    for attempt in range(2):
        r = q.request_history_kline(code, start=START, end=END, ktype=KLType.K_DAY,
                                    autype=AuType.QFQ, max_count=30)
        if r[0] == 0:
            df = r[1]
            out[code] = {"name": name, "bars": [
                {"d": str(row["time_key"])[:10], "c": float(row["close"]),
                 "h": float(row["high"]), "l": float(row["low"])}
                for _, row in df.iterrows()]}
            print(f"OK {code} {name} {len(df)}")
            break
        else:
            print(f"ERR {code} {name} -> {r[1]}")
            time.sleep(1.2)
    time.sleep(0.25)
q.close()
json.dump(out, open(r"F:\Projects\AI\MaplePublicArticles\404k-weekly\scripts\_px_1018.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("DONE", len(out), "/", len(CODES))
