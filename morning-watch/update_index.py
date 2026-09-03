# -*- coding: utf-8 -*-
"""
update_index.py — 关注列表晨报 入口页更新脚本
扫描 morning-watch/data/report_*.html，重建 index.html 的报告列表
"""
import os, re, glob, datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
INDEX = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html')
MAX_ITEMS = 30


def extract_meta(md_path):
    try:
        with open(md_path, encoding='utf-8') as f:
            lines = f.read().split('\n')
    except Exception:
        return '', ''
    title, subtitle = '', ''
    for line in lines:
        s = line.strip()
        if not title and s.startswith('# '):
            title = s.lstrip('# ').strip()
        elif s.startswith('> '):
            subtitle = s.lstrip('> ').strip()
            break
    return title, subtitle


def build_items():
    files = sorted(glob.glob(os.path.join(DATA_DIR, 'report_*.html')), reverse=True)[:MAX_ITEMS]
    items = []
    for p in files:
        base = os.path.basename(p)
        date_str = base[len('report_'):-len('.html')]
        md_path = os.path.join(DATA_DIR, f'report_{date_str}.md')
        title, meta = extract_meta(md_path)
        try:
            d = datetime.date.fromisoformat(date_str)
            day, mon = str(d.day), d.strftime('%b')
        except Exception:
            day, mon = date_str, ''
        items.append(f'''    <a class="report-item" href="data/{base}">
      <div class="report-date"><div class="day">{day}</div><div class="mon">{mon}</div></div>
      <div class="report-body"><div class="report-title">{title}</div><div class="report-meta">{meta[:80]}</div></div>
      <div class="arrow">›</div>
    </a>''')
    return '\n'.join(items)


def main():
    with open(INDEX, encoding='utf-8') as f:
        html = f.read()
    items = build_items()
    html = re.sub(r'<div class="report-list" id="reportList">.*?</div>',
                  f'<div class="report-list" id="reportList">\n{items}\n  </div>',
                  html, flags=re.S)
    # 移除 fallback script
    html = re.sub(r'<script>\s*// 由 update_index\.py.*?</script>', '', html, flags=re.S)
    with open(INDEX, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"索引已更新: {len(items)} 份报告")


if __name__ == '__main__':
    main()
