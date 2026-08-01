import markdown
import sys
import os

md_file = "D:/AI/MaplePublicArticles/404k-daily/data/report_2026-07-31.md"
html_file = "D:/AI/MaplePublicArticles/404k-daily/data/report_2026-07-31.html"
date_str = "2026-07-31"

with open(md_file, "r", encoding="utf-8") as f:
    md_content = f.read()

md = markdown.Markdown(extensions=["tables", "fenced_code", "codehilite"], output_format="html")
body_html = md.convert(md_content)

html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta property="og:title" content="404K半导体日报 | {date_str}">
<meta property="og:type" content="article">
<title>404K半导体日报 | {date_str}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    background: #0d1117;
    color: #c9d1d9;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    line-height: 1.7;
    max-width: 900px;
    margin: 0 auto;
    padding: 20px 24px 40px;
}}
a {{ color: #58a6ff; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
.back-link {{
    display: inline-block;
    margin-bottom: 24px;
    padding: 6px 14px;
    border: 1px solid #30363d;
    border-radius: 6px;
    font-size: 14px;
    color: #8b949e;
    transition: all 0.2s;
}}
.back-link:hover {{
    background: #21262d;
    color: #c9d1d9;
    text-decoration: none;
}}
h1 {{
    font-size: 28px;
    color: #f0f6fc;
    border-bottom: 2px solid #30363d;
    padding-bottom: 12px;
    margin: 16px 0 20px;
}}
h2 {{
    font-size: 22px;
    color: #e6edf3;
    margin: 32px 0 16px;
    padding-bottom: 6px;
    border-bottom: 1px solid #21262d;
}}
h3 {{
    font-size: 18px;
    color: #e6edf3;
    margin: 24px 0 12px;
}}
h4 {{
    font-size: 16px;
    color: #d2d8e0;
    margin: 20px 0 10px;
}}
p {{ margin: 10px 0; }}
strong {{ color: #f0f6fc; }}
em {{ color: #8b949e; }}
blockquote {{
    border-left: 3px solid #58a6ff;
    margin: 16px 0;
    padding: 8px 16px;
    background: #161b22;
    color: #8b949e;
    border-radius: 0 4px 4px 0;
}}
blockquote p {{ margin: 4px 0; }}
table {{
    width: 100%;
    border-collapse: collapse;
    margin: 16px 0;
    font-size: 14px;
}}
th {{
    background: #21262d;
    color: #f0f6fc;
    padding: 10px 12px;
    text-align: left;
    border: 1px solid #30363d;
    font-weight: 600;
}}
td {{
    padding: 8px 12px;
    border: 1px solid #30363d;
    vertical-align: top;
}}
tr:nth-child(even) td {{ background: #161b22; }}
tr:hover td {{ background: #1c2533; }}
code {{
    background: #161b22;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 13px;
    color: #f0883e;
}}
pre {{
    background: #161b22;
    padding: 16px;
    border-radius: 6px;
    overflow-x: auto;
    margin: 12px 0;
    border: 1px solid #30363d;
}}
pre code {{ background: none; padding: 0; color: #c9d1d9; }}
hr {{
    border: none;
    border-top: 1px solid #21262d;
    margin: 32px 0;
}}
ul, ol {{ margin: 8px 0 8px 24px; }}
li {{ margin: 4px 0; }}
.footer {{
    margin-top: 40px;
    padding-top: 16px;
    border-top: 1px solid #21262d;
    color: #484f58;
    font-size: 12px;
    text-align: center;
}}
</style>
</head>
<body>
<a class="back-link" href="../index.html">← 返回日报列表</a>
{body_html}
<div class="footer">404K半导体日报 | 数据来源：ima知识库"404k-0728" | 仅供参考，不构成投资建议</div>
</body>
</html>"""

with open(html_file, "w", encoding="utf-8") as f:
    f.write(html_template)

print(f"HTML written to: {html_file}")
print(f"Size: {os.path.getsize(html_file)} bytes")
