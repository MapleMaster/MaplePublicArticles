import json,sys
sys.stdout.reconfigure(encoding="utf-8")
d=json.load(open("_px_1025.json",encoding="utf-8"))
keys=["SH.688072","SH.588710","SZ.300757","SH.688008","SZ.000657","SZ.159570","SH.588200",
      "HK.06869","HK.01888","HK.06166","HK.00100","HK.01548"]
for k in keys:
    if k not in d: continue
    b=[(x["d"][5:],x["c"]) for x in d[k]["bars"] if x["d"]>="2026-10-16"]
    print(f"{d[k]['name']:<12}", " ".join(f"{a}:{c:.3f}" for a,c in b))
print()
