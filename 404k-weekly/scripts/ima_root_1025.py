# -*- coding: utf-8 -*-
"""列出 ima 知识库 404k-0728 根目录全部条目（含日期文件夹）"""
import json, os, sys, time, urllib.request

BASE = "https://ima.qq.com/openapi/wiki/v1/"
CID = open(os.path.expanduser("~/.config/ima/client_id")).read().strip()
KEY = open(os.path.expanduser("~/.config/ima/api_key")).read().strip()


def api(path, body, retry=3):
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    for i in range(retry):
        try:
            req = urllib.request.Request(BASE + path, data=data, method="POST")
            req.add_header("ima-openapi-clientid", CID)
            req.add_header("ima-openapi-apikey", KEY)
            req.add_header("Content-Type", "application/json")
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            print(f"  [retry {i+1}] {e}", file=sys.stderr)
            time.sleep(2)
    return {"code": -1, "msg": "failed"}


def main():
    r = api("search_knowledge_base", {"query": "404k-0728", "limit": 20})
    kb_id = None
    items = r.get("data", {}).get("info_list") or r.get("data", {}).get("knowledge_base_list") or []
    for it in items:
        name = it.get("kb_name") or it.get("name") or ""
        if "404k-0728" in name.lower().replace(" ", ""):
            kb_id = it.get("kb_id") or it.get("id")
            print("KB HIT:", name, kb_id)
            break
    if not kb_id:
        print("search fail:", json.dumps(r, ensure_ascii=False)[:800])
        return

    root = []
    cursor = ""
    while True:
        body = {"knowledge_base_id": kb_id, "limit": 50}
        if cursor:
            body["cursor"] = cursor
        r = api("get_knowledge_list", body)
        d = r.get("data", {})
        for it in d.get("knowledge_list") or []:
            root.append({
                "name": it.get("name") or it.get("title") or "",
                "id": it.get("folder_id") or it.get("id") or it.get("media_id") or "",
                "type": it.get("media_type") or it.get("type"),
            })
        cursor = d.get("next_cursor") or ""
        if d.get("is_end") or not cursor:
            break
        time.sleep(0.4)
    print("root count:", len(root))
    for x in root:
        print("  ", x["type"], "|", x["name"], "|", x["id"])
    json.dump({"kb_id": kb_id, "root": root},
              open(r"F:\Projects\AI\MaplePublicArticles\404k-weekly\scripts\_root_1025.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
