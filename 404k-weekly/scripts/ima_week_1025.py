# -*- coding: utf-8 -*-
"""拉取本周(10/19-10/25) 7 个日期文件夹内全部文档"""
import json, os, sys, time, urllib.request

BASE = "https://ima.qq.com/openapi/wiki/v1/"
CID = open(os.path.expanduser("~/.config/ima/client_id")).read().strip()
KEY = open(os.path.expanduser("~/.config/ima/api_key")).read().strip()
KB = "ima_kb_u1ZGtMIU"

FOLDERS = {
    "2026-10-19": "folder_7517622530743321",
    "2026-10-20": "folder_7518020704408672",
    "2026-10-21": "folder_7518351798572538",
    "2026-10-22": "folder_7518709883076916",
    "2026-10-23": "folder_7519074577833921",
    "2026-10-24": "folder_7519443068409785",
    "2026-10-25": "folder_7519802155358484",
}


def api(path, body, retry=4):
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
    return {"code": -1}


def main():
    all_data = {}
    total = 0
    for date, fid in FOLDERS.items():
        files = []
        cursor = ""
        while True:
            body = {"knowledge_base_id": KB, "folder_id": fid, "limit": 50}
            if cursor:
                body["cursor"] = cursor
            r = api("get_knowledge_list", body)
            if r.get("code") != 0:
                print(date, "ERR", json.dumps(r, ensure_ascii=False)[:300])
                break
            d = r.get("data", {})
            for it in d.get("knowledge_list") or []:
                files.append({
                    "name": it.get("name") or it.get("title") or "",
                    "media_id": it.get("media_id") or it.get("id") or "",
                    "media_type": it.get("media_type") or it.get("type"),
                    "ctime": it.get("create_time") or it.get("ctime") or "",
                })
            cursor = d.get("next_cursor") or ""
            if d.get("is_end") or not cursor:
                break
            time.sleep(0.35)
        all_data[date] = files
        total += len(files)
        print(f"{date}: {len(files)} 份")
        time.sleep(0.35)
    print("TOTAL:", total)
    out = r"F:\Projects\AI\MaplePublicArticles\404k-weekly\scripts\_week_1025.json"
    json.dump(all_data, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("saved", out)


if __name__ == "__main__":
    main()
