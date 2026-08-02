# -*- coding: utf-8 -*-
"""Render 404K weekly report markdown to HTML (dark theme)"""
import markdown, os

MD = r'D:/AI/MaplePublicArticles/404k-weekly/data/report_2026-08-02.md'
HTML = r'D:/AI/MaplePublicArticles/404k-weekly/data/report_2026-08-02.html'
TITLE = '404K持仓情报周报 | 2026-08-02'

with open(MD, 'r', encoding='utf-8') as f:
    text = f.read()

body = markdown.markdown(text, extensions=['tables', 'fenced_code'])

html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>''' + TITLE + '''</title>
<meta property="og:title" content="''' + TITLE + '''">
<meta property="og:image" content="https://reports.xiaoyiyi.wang/assets/og-share.jpg">
<style>
body{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;max-width:900px;margin:0 auto;padding:20px;background:#0d1117;color:#c9d1d9;line-height:1.7;font-size:15px}
a{color:#58a6ff}h1{border-bottom:1px solid #30363d;padding-bottom:8px;font-size:1.5em}
h2{margin-top:32px;color:#f0b90b;font-size:1.15em;border-bottom:1px solid #21262d;padding-bottom:6px}
h3{margin-top:20px;color:#58a6ff;font-size:1.05em}
h4{margin-top:14px;color:#c9d1d9;font-size:.98em}
table{border-collapse:collapse;width:100%;margin:12px 0;font-size:.85em}
th,td{border:1px solid #30363d;padding:8px 12px;text-align:left}
th{background:#161b22;color:#f0b90b}
tr:nth-child(even){background:#0f1419}
code{background:#161b22;padding:2px 6px;border-radius:4px}
strong{color:#f0b90b}
blockquote{border-left:3px solid #30363d;padding-left:16px;margin:8px 0;color:#8b949e}
ul{padding-left:24px}li{margin:4px 0}
hr{border:none;border-top:1px solid #21262d;margin:24px 0}
.back{display:inline-block;margin-bottom:16px;color:#8b949e;text-decoration:none}
.back:hover{color:#c9d1d9}
@media (max-width:600px){body{padding:12px;font-size:14px}table{font-size:.78em}}
</style>
</head>
<body>
<a class="back" href="../index.html">← 返回列表</a>
''' + body + '''
</body>
</html>'''

with open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)
print('HTML written:', HTML, os.path.getsize(HTML), 'bytes')
