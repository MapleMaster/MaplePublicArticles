# -*- coding: utf-8 -*-
"""本周(10/19-10/25)持仓与跟踪标的价格序列 —— 富途 OpenAPI 直连"""
import json, sys, time, logging
sys.stdout.reconfigure(encoding="utf-8")
logging.getLogger("futu").setLevel(logging.WARNING)
from futu import OpenQuoteContext, KLType, AuType

CODES = {
    # A股 在持仓（PORTFOLIO V2026-10-14-1446）
    "SZ.300757": "罗博特科", "SH.688072": "拓荆科技", "SH.588710": "科半导体ETF",
    "SZ.159570": "创新药HK", "SZ.000657": "中钨高新", "SH.688008": "澜起科技",
    "SH.588200": "科创芯片ETF",
    # A股 产业链参照（已清仓/未持仓）
    "SZ.300308": "中际旭创", "SZ.300394": "天孚通信", "SH.600183": "生益科技",
    "SZ.300604": "长川科技", "SH.600176": "中国巨石", "SZ.159516": "半导设备ETF",
    "SH.515880": "通信ETF", "SZ.300502": "新易盛", "SZ.002463": "沪电股份",
    "SZ.002913": "奥士康", "SH.603986": "兆易创新", "SH.688825": "长鑫科技",
    # 港股 在持仓
    "HK.06869": "长飞光纤光缆", "HK.01888": "建滔积层板", "HK.00100": "MINIMAX-W",
    "HK.01548": "金斯瑞生物科技",
    # 港股 参照
    "HK.00148": "建滔集团", "HK.00522": "ASMPT",
    # 美股 在持仓（IB 大/小号 + 富途）
    "US.SKHY": "SK海力士ADR", "US.MU": "美光", "US.BE": "Bloom Energy",
    "US.AVGO": "博通", "US.TSM": "台积电", "US.S": "SentinelOne", "US.IBKR": "盈透",
    "US.COHR": "Coherent", "US.ATI": "ATI", "US.CLS": "Celestica", "US.INTC": "英特尔",
    "US.BA": "波音", "US.ALAB": "Astera Labs", "US.WEAT": "小麦ETF", "US.SOFI": "SoFi",
    "US.AAPL": "苹果", "US.ASTS": "AST SpaceMobile", "US.VST": "Vistra", "US.CIEN": "Ciena",
    "US.NBIS": "Nebius", "US.HWM": "Howmet", "US.MRVL": "迈威尔", "US.RKLB": "Rocket Lab",
    "US.JPM": "摩根大通", "US.COST": "好市多", "US.TWST": "Twist Bio",
    "US.GDXU": "3x金矿ETF", "US.GOOX": "2x谷歌ETF", "US.MSTU": "2xMSTR ETF",
    "US.IONQ": "IonQ", "US.MSTR": "Strategy",
    # 美股 参照
    "US.SNDK": "闪迪", "US.DRAM": "DRAM ETF", "US.DISK": "DISK ETF", "US.TQQQ": "TQQQ",
    "US.NVDA": "英伟达", "US.WDC": "西部数据", "US.STX": "希捷", "US.CRVW": "CoreWeave",
    "US.LRCX": "泛林", "US.AMAT": "应用材料", "US.TER": "泰瑞达", "US.LITE": "Lumentum",
    "US.CRDO": "Credo",
    # 指数
    "SH.000001": "上证综指", "SZ.399001": "深证成指", "SZ.399006": "创业板指",
    "SH.000688": "科创50", "SH.000300": "沪深300",
    "HK.800000": "恒生指数", "HK.800700": "恒生科技",
}

START, END = "2026-10-08", "2026-10-25"
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
    time.sleep(0.2)
q.close()
json.dump(out, open(r"F:\Projects\AI\MaplePublicArticles\404k-weekly\scripts\_px_1025.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("DONE", len(out), "/", len(CODES))
