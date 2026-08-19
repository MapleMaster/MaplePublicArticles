# -*- coding: utf-8 -*-
"""
update_index.py — 每日盘后全景 入口页更新脚本
=============================================
用法：
    python update_index.py            # 扫描 data/report_*.html，重建 index.html 的报告列表
    python update_index.py --dry-run  # 只打印将要生成的内容，不写文件

- 扫描 panorama/data/ 下所有 report_YYYY-MM-DD.html（倒序）
- 提取每份的标题与摘要（从对应 .md 的第一段/生成时间行）
- 在 index.html 的 reportList 区域插入 report-item 列表，最多 30 份
- 样式保持不变（只改列表区内容）
"""
import os
import re
import glob
import sys

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
INDEX = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html')
MAX_ITEMS = 30


def extract_meta(md_path):
    """从 md 提取标题行和摘要行。"""
    try:
        with open(md_path, encoding='utf-8') as f:
            lines = f.read().split('\n')
    except Exception:
        return '每日盘后全景', ''
    title = ''
    subtitle = ''
    for line in lines:
        s = line.strip()
        if not title and s.startswith('# '):
            title = s.lstrip('# ').strip()
        elif s.startswith('> '):
            subtitle = s.lstrip('> ').strip()
            break
    return title, subtitle


def build_items():
    html_files = sorted(glob.glob(os.path.join(DATA_DIR, 'report_*.html')))
    items = []
    for p in reversed(html_files):
        base = os.path.basename(p)
        date_str = base[len('report_'):-len('.html')]
        md_path = os.path.join(DATA_DIR, f'report_{date_str}.md')
        title, meta = extract_meta(md_path)
        if not title:
            title = f'每日盘后全景 | {date_str}'
        # 日期拆分
        try:
            y, m, d = date_str.split('-')
            mon, day = int(m), int(d)
        except Exception:
            mon, day = '', ''
        # meta 截断到 ~90 字
        if meta:
            meta = meta[:90]
        else:
            meta = '每日盘后全景'
        item = (
            f'    <a class="report-item" href="data/{base}">\n'
            f'      <div class="report-date">\n'
            f'        <div class="day">{day}</div>\n'
            f'        <div class="mon">{mon}月</div>\n'
            f'      </div>\n'
            f'      <div class="report-body">\n'
            f'        <div class="report-title">{title}</div>\n'
            f'        <div class="report-meta">{meta}</div>\n'
            f'      </div>\n'
            f'      <span class="arrow">›</span>\n'
            f'    </a>'
        )
        items.append(item)
        if len(items) >= MAX_ITEMS:
            break
    return items


def update_index(items, dry_run=False):
    with open(INDEX, encoding='utf-8') as f:
        html = f.read()

    if items:
        list_html = '<div class="report-list" id="reportList">\n\n' + '\n\n'.join(items) + '\n\n  </div>'
    else:
        list_html = (
            '<div class="report-list" id="reportList">\n\n'
            '    <div class="empty-state">\n'
            '      <span class="icon">🗺️</span>\n'
            '      <div class="title">报告生成中</div>\n'
            '      <div class="desc">每日盘后全景报告将于交易日 19:30 自动生成</div>\n'
            '    </div>\n\n  </div>')

    # 替换 reportList 区块（非贪婪到第一个 </div> 之后的结尾：用注释锚点更稳）
    pat = re.compile(
        r'<div class="report-list" id="reportList">.*?</div>\n\s*</div>',
        re.DOTALL)
    if not pat.search(html):
        print('ERROR: 未找到 reportList 区块')
        sys.exit(1)
    new_html = pat.sub(list_html, html, count=1)

    if dry_run:
        print(list_html[:600])
        return
    with open(INDEX, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print(f'✓ 已更新 index.html，报告条目 {len(items)} 份')


if __name__ == '__main__':
    items = build_items()
    update_index(items, dry_run='--dry-run' in sys.argv)
