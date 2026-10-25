# -*- coding: utf-8 -*-
"""对本周文档做分类统计与关键词筛选"""
import json, re, collections

SRC = r"F:\Projects\AI\MaplePublicArticles\404k-weekly\scripts\_week_1025.json"
data = json.load(open(SRC, encoding="utf-8"))

HOLD = {
    "A股": ["中际旭创", "旭创", "InnoLight", "天孚", "TFC", "O-net", "生益", "SYTech", "长川",
            "中国巨石", "巨石", "罗博特科", "拓荆", "澜起", "中钨", "创新药", "科创芯片", "半导体设备ETF",
            "科半导体", "长鑫", "云南锗业"],
    "港股": ["建滔", "Kingboard", "长飞", "YOFC", "剑桥科技", "MINIMAX", "金斯瑞", "胜宏"],
    "美股": ["美光", "Micron", "MU", "海力士", "SKHynix", "SKHY", "铠侠", "Kioxia", "闪迪", "Sandisk", "SNDK",
            "Marvell", "MRVL", "Intel", "INTC", "Nebius", "NBIS", "LRCX", "拉姆", "AMAT", "应用材料",
            "Teradyne", "泰瑞达", "TER", "台积电", "TSM", "Bloom", "BE", "Ciena", "CIEN", "Celestica", "CLS",
            "博通", "AVGO", "Coherent", "COHR", "Astera", "ALAB", "SanDisk"],
}

PRICE = ["GPU租赁", "租赁价格", "H100", "H200", "H300", "B200", "GB200", "Token", "token支出",
         "NAND", "DRAM", "现货价", "合约价", "SSD", "eSSD", "MLCC", "覆铜板", "CCL", "涨价", "报价", "价格"]

RATING = ["目标价", "上调", "下调", "评级", "买入", "增持", "中性", "减持", "upgrade", "downgrade",
          "首次覆盖", "首评", "重申", "PT"]

THEME = {
    "光模块/CPO": ["光模块", "CPO", "NPO", "LPO", "光互连", "硅光", "800G", "1.6T", "3.2T", "光通信"],
    "存储": ["存储", "HBM", "DRAM", "NAND", "eSSD", "HDD", "内存", "颗粒", "LPDDR", "DDR5", "CXL"],
    "半导体设备": ["设备", "WFE", "先进封装", "刻蚀", "薄膜", "沉积", "量测", "CoWoS", "检测"],
    "PCB/覆铜板/材料": ["PCB", "覆铜板", "CCL", "ABF", "铜箔", "玻纤", "树脂", "载板", "基板"],
    "云商CAPEX": ["CAPEX", "CSP", "资本开支", "超大规模", "云厂", "云计算"],
    "AI算力/neocloud": ["算力", "neocloud", "GPU", "英伟达", "Nvidia", "数据中心", "机柜", "Rubin"],
    "上游涨价": ["InP", "磷化铟", "石英", "Q布", "MLCC", "被动元件", "涨价", "缺货", "紧缺"],
    "光纤光缆": ["光纤", "光缆", "空芯"],
    "韩国出口": ["韩国", "出口", "韩股", "KOSPI", "三星电子"],
    "财报": ["财报", "业绩", "Q3", "三季报", "指引", "earnings"],
}
BANK = ["Nomura", "野村", "UBS", "瑞银", "Citi", "花旗", "Goldman", "高盛", "Morgan", "摩根", "大摩", "小摩",
        "JPM", "美银", "BofA", "Deutsche", "德银", "Jefferies", "巴克莱", "Barclays", "汇丰", "HSBC",
        "中金", "中信", "天风", "国金", "东吴", "华泰", "招商", "广发", "国泰海通", "东方证券", "开源", "民生", "申万"]
OWN = ["404K Semi-Ai", "404K科技", "404K", "Semi-Ai"]

stats = collections.Counter()
hit = collections.defaultdict(list)
all_docs = []
for date, files in data.items():
    for f in files:
        n = f["name"]
        mt = f.get("media_type")
        all_docs.append((date, n, mt))
        # 类型判断
        if re.search(r"\.pdf$", n, re.I) or "PDF" in n:
            stats["PDF"] += 1
        elif re.search(r"\.(png|jpg|jpeg|webp)$", n, re.I) or mt == 99 or mt == 2:
            stats["图片"] += 1
        else:
            stats["其他"] += 1
        tags = []
        for g, kws in HOLD.items():
            if any(k.lower() in n.lower() for k in kws):
                tags.append("持仓:" + g)
        if any(k.lower() in n.lower() for k in PRICE):
            tags.append("价格")
        if any(k.lower() in n.lower() for k in RATING):
            tags.append("评级")
        for g, kws in THEME.items():
            if any(k.lower() in n.lower() for k in kws):
                tags.append("主题:" + g)
        if any(k.lower() in n.lower() for k in BANK):
            tags.append("投行")
        if any(k.lower() in n.lower() for k in OWN):
            tags.append("404K自主")
        for t in set(tags):
            hit[t].append((date, n))
        f["tags"] = sorted(set(tags))

print("=== 总量:", len(all_docs), dict(stats))
print()
for k in sorted(hit, key=lambda x: -len(hit[x])):
    print(f"[{k}] {len(hit[k])}")
print()
# 重点文档明细（持仓+价格+评级+投行）
print("=" * 30, "重点明细", "=" * 30)
for date, files in data.items():
    for f in files:
        if any(t.startswith("持仓") or t in ("价格", "评级", "投行") for t in f["tags"]):
            print(date, "|", ",".join(f["tags"]), "|", f["name"][:130])

json.dump(data, open(SRC, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
