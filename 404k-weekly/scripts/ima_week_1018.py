# -*- coding: utf-8 -*-
"""拉取本周 7 个日期文件夹内全部文档"""
import json, os, sys, time, urllib.request

BASE = "https://ima.qq.com/openapi/wiki/v1/"
CID = open(os.path.expanduser("~/.config/ima/client_id")).read().strip()
KEY = open(os.path.expanduser("~/.config/ima/api_key")).read().strip()
KB = "J96LReGPa7zjyQdnys0J4HiM-0gynB0gBx-xqh28Z7o="

FOLDERS = {
    "2026-10-12": "folder_7515099422004676",
    "2026-10-13": "folder_7515459075185893",
    "2026-10-14": "folder_7515808854971615",
    "2026-10-15": "folder_7516168449431613",
    "2026-10-16": "folder_7516534259848009",
    "2026-10-17": "folder_7516917623427590",
    "2026-10-18": "folder_7517259232711423",
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
                print(date, "ERR", r)
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
            time.sleep(0.4)
        all_data[date] = files
        total += len(files)
        print(f"{date}: {len(files)} 份")
        time.sleep(0.4)
    print("TOTAL:", total)
    json.dump(all_data, open(r"F:\Projects\AI\MaplePublicArticles\404k-weekly\scripts\_week_1018.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
