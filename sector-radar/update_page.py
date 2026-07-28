# -*- coding: utf-8 -*-
"""
sector-radar 页面更新脚本（预渲染 HTML 版）

用法：
    python update_page.py <md_dir> [output_html]

- 扫描 md_dir 下所有 YYYY-MM-DD.md 报告
- 用 Python markdown 库预渲染成 HTML 片段（按 ## 切分包 md-card）
- 从现有 output_html 提取 head（含全部 CSS）作模板，重新生成 index.html
- 最新日期内容首屏直出，其余放 <template>，JS 仅切换（零运行时 md 解析）
- 默认只保留最近 30 份，避免页面无限膨胀

依赖：markdown 库（pip install markdown）
"""
import re
import os
import sys
import glob
import markdown

MAX_REPORTS = 30
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def is_list_line(line):
    return bool(re.match(r'^\s*[-]\s', line)) or bool(re.match(r'^\s*\d+\.\s', line))


def fix_lists(md_text):
    """列表项紧跟在非空段落后面时补一个空行，让 markdown 正确识别列表块。"""
    lines = md_text.split('\n')
    out = []
    for i, line in enumerate(lines):
        cur_list = is_list_line(line)
        if i > 0:
            prev = lines[i - 1]
            prev_list = is_list_line(prev)
            prev_empty = prev.strip() == ''
            cur_empty = line.strip() == ''
            if cur_list and not prev_list and not prev_empty:
                out.append('')
            if not cur_list and not cur_empty and prev_list:
                out.append('')
        out.append(line)
    return '\n'.join(out)


def render_to_cards(md_text):
    md_ext = markdown.Markdown(extensions=['sane_lists'])
    body = md_ext.convert(fix_lists(md_text.strip()))
    md_ext.reset()
    parts = re.split(r'(?=<h2)', body)
    cards = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        cards.append('<div class="md-card"><div class="md">' + p + '</div></div>')
    return '\n      '.join(cards)


def extract_head(html_text):
    """从现有 index.html 提取 <head>...</head> 内容（含全部 CSS，不含 DOCTYPE/html 标签）。

    用非贪婪匹配取第一个 <head>...</head>，避免历史文件中 DOCTYPE 重复导致的污染。
    """
    m = re.search(r'<head>(.*?)</head>', html_text, re.DOTALL)
    if not m:
        raise RuntimeError('无法从 index.html 提取 <head>...</head>')
    return m.group(1)


BODY_TEMPLATE = '''<body>

<div class="bg-img"></div>
<div class="scan"></div>

<div class="page">

  <header class="hero">
    <div class="hero-badge">
      <span class="blink"></span>
      <span>SECTOR RADAR</span>
    </div>
    <h1><span class="g">📡 A股板块雷达</span></h1>
    <div class="sub">每日盘后总结 · 大盘多空 · 四档分类</div>
  </header>

  <a class="back-link" href="../index.html">‹ 返回主页</a>

  <div class="date-switch" id="date-switch"></div>

  <div id="report-area" class="show">
      __LATEST_CARDS__
  </div>

  <footer class="footer">
    <p>
      <span class="hl">🦅 华尔街之鹰</span> · 雷达由 <span class="lotus">🪷 小荷</span> 自动生成<br>
      数据来源：腾讯自选股（westock-data）· 不构成投资建议
    </p>
  </footer>

</div>

    __TEMPLATES__

<script>
(function(){
  var dates = __DATES_JS__;
  var switchEl = document.getElementById('date-switch');
  var reportEl = document.getElementById('report-area');
  var current = '__LATEST__';

  dates.forEach(function(d){
    var btn = document.createElement('button');
    btn.className = 'date-btn' + (d === current ? ' active' : '');
    btn.setAttribute('data-date', d);
    var label = d.slice(5).replace('-','/');
    if(d.indexOf('-午盘') > -1){ label = label.replace('-午盘','') + ' 午'; }
    btn.textContent = label;
    btn.onclick = function(){ selectDate(d); };
    switchEl.appendChild(btn);
  });

  function selectDate(d){
    if(d === current) return;
    current = d;
    switchEl.querySelectorAll('.date-btn').forEach(function(b){
      b.classList.toggle('active', b.getAttribute('data-date') === d);
    });
    var tplId = 'tpl-' + d.replace('-午盘','-mid');
    var tpl = document.getElementById(tplId);
    if(!tpl) return;
    reportEl.classList.remove('show');
    reportEl.style.opacity = '0';
    setTimeout(function(){
      reportEl.innerHTML = '';
      reportEl.appendChild(document.importNode(tpl.content, true));
      requestAnimationFrame(function(){
        reportEl.classList.add('show');
        reportEl.style.opacity = '';
      });
    }, 180);
  }
})();
</script>

</body>'''


def main():
    if len(sys.argv) < 2:
        print('用法: python update_page.py <md_dir> [output_html]')
        sys.exit(1)
    md_dir = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(SCRIPT_DIR, 'index.html')

    # 扫描所有 YYYY-MM-DD.md 和 YYYY-MM-DD-午盘.md
    files = glob.glob(os.path.join(md_dir, '20??-??-??.md')) + \
            glob.glob(os.path.join(md_dir, '20??-??-??-午盘.md'))
    if not files:
        print('错误：在', md_dir, '未找到 YYYY-MM-DD.md 报告')
        sys.exit(1)

    # 按日期降序；同日收盘版排在午盘版后面（收盘版更新，应为首屏）
    dated = []
    for f in files:
        b = os.path.basename(f)
        m = re.match(r'(\d{4}-\d{2}-\d{2})(-午盘)?', b)
        if m:
            # 午盘用 -0，收盘用 -1，降序排列时收盘在前（首屏）
            sort_key = m.group(1) + ('-0' if m.group(2) else '-1')
            dated.append((sort_key, m.group(1) + (m.group(2) or ''), f))
    dated.sort(key=lambda x: x[0], reverse=True)
    dated = dated[:MAX_REPORTS]
    dates = [d for _, d, _ in dated]
    latest = dates[0]
    print('发现报告:', dates, '首屏:', latest)

    # 渲染每份
    cards_map = {}
    for _, d, f in dated:
        with open(f, 'r', encoding='utf-8') as fh:
            cards_map[d] = render_to_cards(fh.read())

    # 提取 head（从现有 index.html，保证样式跟随更新）
    head = ''
    if os.path.exists(out):
        with open(out, 'r', encoding='utf-8') as fh:
            head = extract_head(fh.read())
    if not head:
        print('错误：无法提取 head，请确保 index.html 存在且含 </style></head>')
        sys.exit(1)

    # 组装 templates
    templates = []
    for d in dates:
        tpl_id = 'tpl-' + d.replace('-午盘', '-mid')
        templates.append('<template id="' + tpl_id + '">\n      ' + cards_map[d] + '\n    </template>')
    templates_str = '\n    '.join(templates)
    dates_js = '[' + ','.join("'" + d + "'" for d in dates) + ']'

    body = (BODY_TEMPLATE
            .replace('__LATEST_CARDS__', cards_map[latest])
            .replace('__TEMPLATES__', templates_str)
            .replace('__DATES_JS__', dates_js)
            .replace('__LATEST__', latest))

    new_html = '<!DOCTYPE html>\n<html lang="zh-CN">\n<head>' + head + '</head>\n' + body + '\n</html>'

    with open(out, 'w', encoding='utf-8') as fh:
        fh.write(new_html)
    print('已写入:', out, '大小:', len(new_html), '字节，含', len(dates), '份报告')


if __name__ == '__main__':
    main()
