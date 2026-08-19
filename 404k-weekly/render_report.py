# -*- coding: utf-8 -*-
"""
render_report.py — 404K持仓情报周报 渲染脚本 v2（投研日报级排版）
=============================================================
用法：
    python render_report.py                # 渲染最近一份周报
    python render_report.py 2026-08-09     # 渲染指定日期
    python render_report.py --all          # 重渲染全部历史周报
"""
import os
import re
import sys
import glob
import markdown
from datetime import datetime, date

sys.path.insert(0, r'F:/Projects/AI/MaplePublicArticles/scripts')
from pretty_report import render_article, postprocess_body, build_toc, preprocess_md

DATA_DIR = r'F:/Projects/AI/MaplePublicArticles/404k-weekly/data'
SITE_BASE = 'https://reports.xiaoyiyi.wang/404k-weekly'
BADGE = '404K SEMI · WEEKLY'
TITLE = '404K 持仓情报周报'
HOME = '../index.html'
FOOTER = '数据来源：404K Semi-AI 知识库（海外投行研报 / 404K自主报告 / 资讯汇总）· 持仓数据以 PORTFOLIO.md 为准'

WEEKDAYS = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']


def parse_md(md_text, date_str):
    subtitle = '周度深度整合 · 持仓追踪 / 价格时间序列 / 评级台账'
    for line in md_text.split('\n'):
        line = line.strip()
        if line.startswith('>'):
            subtitle = line.lstrip('> ').strip('| ').strip()
            break
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        wd = WEEKDAYS[dt.weekday()]
    except Exception:
        wd = ''
    return subtitle, wd


def render_one(md_path, html_path, all_dates=None):
    date_str = os.path.basename(md_path)[len('report_'):-3]
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    md = markdown.Markdown(extensions=['tables', 'fenced_code', 'sane_lists'])
    body_html = md.convert(preprocess_md(md_text))
    md.reset()
    body_html = postprocess_body(body_html)
    toc = build_toc(body_html)

    subtitle, wd = parse_md(md_text, date_str)
    date_label = f'{date_str} · {wd}' if wd else date_str

    prev_html = next_html = None
    if all_dates:
        idx = all_dates.index(date_str) if date_str in all_dates else -1
        if idx > 0:
            prev_html = f'report_{all_dates[idx-1]}.html'
        if 0 <= idx < len(all_dates) - 1:
            next_html = f'report_{all_dates[idx+1]}.html'

    og_desc = f'{TITLE} {date_str} - 持仓标的一周动态、价格数据时间序列与投行评级台账'
    html = render_article(
        badge=BADGE, title=TITLE, date_label=date_label, subtitle=subtitle,
        body_html=body_html, toc=toc, prev_html=prev_html, next_html=next_html,
        home_href=HOME, footer_note=FOOTER,
        og_desc=og_desc, og_url=f'{SITE_BASE}/data/report_{date_str}.html',
    )
    with open(html_path, 'w', encoding='utf-8-sig') as f:
        f.write(html)
    print(f'✓ {date_str}: {len(html)} bytes')


def main():
    args = sys.argv[1:]
    md_files = sorted(glob.glob(os.path.join(DATA_DIR, 'report_*.md')))
    all_dates = [os.path.basename(p)[len('report_'):-3] for p in md_files]

    if '--all' in args:
        for md_path in md_files:
            date_str = os.path.basename(md_path)[len('report_'):-3]
            html_path = os.path.join(DATA_DIR, f'report_{date_str}.html')
            render_one(md_path, html_path, all_dates)
        print(f'完成：共重渲染 {len(md_files)} 份周报')
        return

    if args and args[0] != '--all':
        date_str = args[0]
    else:
        md_files = sorted(glob.glob(os.path.join(DATA_DIR, 'report_*.md')))
        if not md_files:
            print('错误：未找到任何 report_*.md')
            sys.exit(1)
        md_path = md_files[-1]
        date_str = os.path.basename(md_path)[len('report_'):-3]

    md_path = os.path.join(DATA_DIR, f'report_{date_str}.md')
    if not os.path.exists(md_path):
        print(f'错误：{md_path} 不存在')
        sys.exit(1)
    html_path = os.path.join(DATA_DIR, f'report_{date_str}.html')
    render_one(md_path, html_path, all_dates)


if __name__ == '__main__':
    main()
