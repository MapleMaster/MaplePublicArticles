"""Convert 404K daily report MD to HTML with dark theme."""
import markdown
import sys
from datetime import datetime

date_str = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime('%Y-%m-%d')
md_path = f'F:/Projects/AI/MaplePublicArticles/404k-daily/data/report_{date_str}.md'
html_path = f'F:/Projects/AI/MaplePublicArticles/404k-daily/data/report_{date_str}.html'

with open(md_path, 'r', encoding='utf-8') as f:
    md_content = f.read()

# Configure markdown with extensions
md = markdown.Markdown(extensions=['tables', 'fenced_code', 'codehilite', 'nl2br'])

# Extract title from first heading
lines = md_content.split('\n')
title_line = lines[0].strip('# ') if lines[0].startswith('#') else f'404K日报 {date_str}'

# Convert markdown to HTML body
body_html = md.convert(md_content)

html_template = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta property="og:title" content="{title_line}">
    <meta property="og:type" content="article">
    <meta name="description" content="404K半导体日报 {date_str} - AI/半导体产业链每日核心信号、持仓动态与风险提示">
    <title>{title_line}</title>
    <style>
        :root {{
            --bg: #0d1117;
            --bg-secondary: #161b22;
            --border: #30363d;
            --text: #c9d1d9;
            --text-secondary: #8b949e;
            --accent: #58a6ff;
            --accent-green: #3fb950;
            --accent-red: #f85149;
            --accent-orange: #d2991d;
            --accent-purple: #a371f7;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background: var(--bg);
            color: var(--text);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
            line-height: 1.7;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px 24px 60px;
        }}
        a {{ color: var(--accent); text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        h1 {{ font-size: 1.8em; border-bottom: 1px solid var(--border); padding-bottom: 12px; margin: 20px 0 16px; }}
        h2 {{ font-size: 1.4em; margin: 32px 0 16px; color: var(--accent); border-bottom: 1px solid var(--border); padding-bottom: 8px; }}
        h3 {{ font-size: 1.15em; margin: 20px 0 10px; color: var(--accent-purple); }}
        h4 {{ font-size: 1.05em; margin: 16px 0 8px; }}
        blockquote {{
            border-left: 3px solid var(--accent);
            padding: 10px 16px;
            margin: 12px 0;
            background: var(--bg-secondary);
            border-radius: 0 6px 6px 0;
            color: var(--text-secondary);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 16px 0;
            font-size: 0.9em;
        }}
        th, td {{
            border: 1px solid var(--border);
            padding: 8px 12px;
            text-align: left;
        }}
        th {{
            background: var(--bg-secondary);
            font-weight: 600;
        }}
        tr:nth-child(even) {{ background: rgba(255,255,255,0.02); }}
        strong {{ color: #f0f6fc; }}
        hr {{ border: none; border-top: 1px solid var(--border); margin: 24px 0; }}
        code {{
            background: var(--bg-secondary);
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.9em;
        }}
        .back-link {{
            display: inline-block;
            margin-bottom: 20px;
            padding: 6px 14px;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 6px;
            color: var(--text-secondary);
            font-size: 0.9em;
        }}
        .back-link:hover {{
            color: var(--accent);
            border-color: var(--accent);
            text-decoration: none;
        }}
        .highlight-positive {{ color: var(--accent-red); }}
        .highlight-negative {{ color: var(--accent-green); }}
        em {{ color: var(--accent-orange); font-style: normal; }}
        ul, ol {{ padding-left: 24px; margin: 8px 0; }}
        li {{ margin: 4px 0; }}
        @media (max-width: 600px) {{
            body {{ padding: 12px 16px 40px; }}
            h1 {{ font-size: 1.4em; }}
            table {{ font-size: 0.8em; }}
            th, td {{ padding: 6px 8px; }}
        }}
    </style>
</head>
<body>
    <a href="../index.html" class="back-link">← 返回日报列表</a>
    {body_html}
    <hr>
    <p style="color: var(--text-secondary); font-size: 0.85em; margin-top: 20px;">
        📌 以上所有内容均来源于404K Semi-AI知识库公开文档，仅供学习参考，不构成投资建议。<br>
        生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')} | 数据日期：{date_str}
    </p>
</body>
</html>'''

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_template)

print(f'HTML generated: {html_path}')
print(f'Size: {len(html_template)} chars')
