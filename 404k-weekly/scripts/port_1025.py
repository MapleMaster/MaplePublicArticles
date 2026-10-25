# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
d = json.load(open("_px_1025.json", encoding="utf-8"))
px = {k: {b["d"]: b["c"] for b in v["bars"]} for k, v in d.items()}
ACCTS = {
 "A股(平安两融)": {"SZ.300757":300,"SH.688072":200,"SH.588710":102600,"SZ.159570":65100,
                 "SZ.000657":1700,"SH.688008":382,"SH.588200":62500},
 "港股通": {"HK.06869":1500,"HK.01888":3000,"HK.06166":800,"HK.00100":340,"HK.01548":2000},
 "IB大号": {"US.SKHY":83,"US.MU":7,"US.BE":25,"US.AVGO":17,"US.TSM":12,"US.S":220,
          "US.IBKR":48.2656,"US.COHR":14,"US.ATI":18,"US.CLS":8,"US.INTC":24,"US.BA":12,
          "US.ALAB":6,"US.WEAT":70,"US.SOFI":100,"US.AAPL":3,"US.ASTS":20,"US.VST":3,"US.CIEN":1},
 "IB小号": {"US.NBIS":81,"US.HWM":50,"US.MRVL":29,"US.SKHY":37,"US.RKLB":87,"US.JPM":10,
          "US.COST":2,"US.IBKR":2.7112},
 "富途大号": {"US.TWST":47,"US.GDXU":47},
 "富途小号": {"US.GDXU":91,"US.GOOX":78,"US.MSTU":108,"US.IONQ":80,"US.MSTR":17},
}
D0, D1 = "2026-10-16", "2026-10-23"
for acct, pos in ACCTS.items():
    v0 = v1 = 0.0
    print(f"\n=== {acct} ===")
    rows = []
    for c, s in pos.items():
        p0, p1 = px[c].get(D0), px[c].get(D1)
        if p0 is None or p1 is None:
            print("  MISS", c, p0, p1); continue
        m0, m1 = p0*s, p1*s
        v0 += m0; v1 += m1
        rows.append((acct, c, d[c]["name"], s, p0, p1, (p1/p0-1)*100, m0, m1))
    for r in sorted(rows, key=lambda x: x[6]):
        print(f"  {r[2]:<14}{r[3]:>10.2f}股 {r[4]:>9.3f}→{r[5]:>9.3f} {r[6]:>7.2f}%  市值 {r[7]:>10,.0f}→{r[8]:>10,.0f}")
    print(f"  → 组合周涨跌 {v1/v0-1:+.2%}   市值 {v0:,.0f} → {v1:,.0f} ({(v1-v0):+,.0f})")
    wr = sum(x[6]*(x[7]/v0) for x in rows)
    print(f"  → 加权校验 {wr:+.2f}%")
