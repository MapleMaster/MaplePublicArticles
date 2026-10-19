# -*- coding: utf-8 -*-
"""拉取 ima 知识库 404k-0728 本周(10/12-10/18)全部文档清单"""
import json, os, sys, time, urllib.request

BASE = "https://ima.qq.com/openapi/wiki/v1/"
CID = open(os.path.expanduser("~/.config/ima/client_id")).read().strip()
KEY = open(os.path.expanduser("~/.config/ima/api_key")).read().strip()


def api(path, body, retry=3):
    url = BASE + path
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    for i in range(retry):
        try:
            req = urllib.request.Request(url, data=data, method="POST")
            req.add_header("ima-openapi-clientid", CID)
            req.add_header("ima-openapi-apikey", KEY)
            req.add_header("Content-Type", "application/json")
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            print(f"  [retry {i+1}] {path} err={e}", file=sys.stderr)
            time.sleep(2)
    return {"code": -1, "msg": "failed"}


def main():
    # 1. 找知识库
    r = api("search_knowledge_base", {"query": "404k-0728", "limit": 20})
    print("search_knowledge_base:", json.dumps(r, ensure_ascii=False)[:800])
    kb_id = None
    items = r.get("data", {}).get("info_list") or r.get("data", {}).get("knowledge_base_list") or []
    for it in items:
        name = it.get("kb_name") or it.get("name") or ""
        if "404k-0728" in name.lower().replace(" ", ""):
            kb_id = it.get("kb_id") or it.get("id")
            print("HIT:", name, kb_id)
            break
    if not kb_id:
        print("FULL:", json.dumps(r, ensure_ascii=False)[:3000])
        return
    out = {"kb_id": kb_id, "root": [], "folders": {}}
    # 2. 根目录列全部
    cursor = ""
    while True:
        body = {"knowledge_base_id": kb_id, "limit": 50}
        if cursor:
            body["cursor"] = cursor
        r = api("get_knowledge_list", body)
        d = r.get("data", {})
        lst = d.get("knowledge_list") or []
        for it in lst:
            out["root"].append({"name": it.get("name") or it.get("title"), "id": it.get("id") or it.get("folder_id") or it.get("media_id"), "type": it.get("media_type") or it.get("type")})
        cursor = d.get("next_cursor") or ""
        if d.get("is_end") or not cursor:
            break
        time.sleep(0.5)
    print("root count:", len(out["root"]))
    for x in out["root"]:
        print("  ", x)
    json.dump(out, open(r"F:\Projects\AI\MaplePublicArticles\404k-weekly\scripts\_root_1018.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
