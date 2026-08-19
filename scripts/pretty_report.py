# -*- coding: utf-8 -*-
"""
pretty_report.py — 统一的「投研日报级」正文页渲染模板
=====================================================
供 404k-daily / 404k-weekly 的渲染脚本共用。

设计语言对齐 AI投研日报（daily-news/stock-invest）：
深色渐变背景 + hero 徽标/渐变标题 + TOC 胶囊导航 + 章节金色标题条 +
圆角表格 + 金边引用卡 + 彩色列表 marker + 阅读进度条 + 前/后篇导航。

用法：
    from pretty_report import render_article
    html = render_article(
        badge='404K SEMI · DAILY',
        title='404K 半导体日报',
        date_label='2026-08-12 · 周三',
        subtitle='生成时间 2026-08-13 05:00 · 文档 74 份 / 重点 19 份',
        body_html=body_html,            # markdown 库渲染后的正文（已做后处理）
        toc=[('id','一、今日核心信号'), ...],   # 可选，章节锚点
        prev_html='report_2026-08-11.html',
        next_html='report_2026-08-13.html',
        home_href='../index.html',
        footer_note='数据来源：404K Semi-AI 知识库',
        og_desc='...',
        og_url='...',
    )

依赖：无（纯字符串拼接）。
"""
import re
import json

# ---------------------------------------------------------------------------
# 章节 emoji 映射：给 markdown 的 h2 章节标题自动配图标
# ---------------------------------------------------------------------------
SECTION_EMOJI = [
    (r'今日核心信号|核心信号', '🔍'),
    (r'持仓个股动态|持仓个股|持仓标的|个股动态', '💼'),
    (r'产业链关键信号|产业链', '🔗'),
    (r'风险提示|风险', '⚠️'),
    (r'数据速览|数据', '📊'),
    (r'附录|文档清单', '📎'),
    (r'价格数据|时间序列', '💰'),
    (r'投行评级|评级变化|评级台账', '🏦'),
    (r'下周关注|关注清单', '🎯'),
    (r'板块交易结论|交易结论|操作纪律', '🎯'),
    (r'大盘多空|多空状态|大盘状态', '📡'),
    (r'底部特征|顶部特征|指标', '🧭'),
    (r'结论|总结', '📌'),
]


def emoji_for_heading(text):
    for pat, emoji in SECTION_EMOJI:
        if re.search(pat, text):
            return emoji
    return '📌'


def preprocess_md(md_text):
    """渲染前修复 markdown 源：给『段落/粗体标题行 后紧跟 `- ` 列表』补空行。

    日报 md 里常见：
        **1. 标题**
        - 数据支撑：xxx
        - 产业链含义：xxx
    中间没有空行，sane_lists 会把 `- ` 行并进段落、列表符号丢失，
    渲染成一大坨连续文本（排版难看的根源之一）。此函数在其间补空行，
    让 markdown 正常解析为 <ul><li>。对表格行 / 标题 / 已有列表 / 引用安全。
    """
    lines = md_text.split('\n')
    out = []
    for i, line in enumerate(lines):
        out.append(line)
        nxt = lines[i + 1] if i + 1 < len(lines) else ''
        cur = line.strip()
        nxt_s = nxt.strip()
        if (cur
                and not cur.startswith(('#', '>', '|'))
                and not cur.startswith(('- ', '* ', '+ '))
                and re.match(r'^\d+\.\s', cur) is None
                and nxt_s.startswith('- ')):
            out.append('')
    return '\n'.join(out)


def build_toc(body_html):
    """从渲染后的 HTML 提取 h2（带 id 的），生成 TOC 条目。"""
    toc = []
    for m in re.finditer(r'<h2 id="([^"]+)">(.*?)</h2>', body_html, re.DOTALL):
        txt = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        toc.append((m.group(1), txt))
    return toc


def postprocess_body(body_html):
    """对 markdown 渲染结果做后处理：
    1. h2 注入 emoji + 锚点 id
    2. table 包 .table-wrap（移动端横向滚动）
    3. 删除第一个 h1（标题已在 hero 呈现）
    """
    # 1. 删除首个 h1（含其后续紧跟的空行）
    body_html = re.sub(r'<h1>.*?</h1>\s*', '', body_html, count=1, flags=re.DOTALL)

    # 2. h2: 加 id + emoji
    def h2_repl(m):
        txt = m.group(1)
        plain = re.sub(r'<[^>]+>', '', txt).strip()
        anchor = 'sec-' + re.sub(r'\s+', '', plain)[:12]
        emoji = emoji_for_heading(plain)
        return f'<h2 id="{anchor}"><span class="sec-emoji">{emoji}</span>{txt}</h2>'
    body_html = re.sub(r'<h2>(.*?)</h2>', h2_repl, body_html, flags=re.DOTALL)

    # 3. table 包横向滚动容器
    def table_repl(m):
        return '<div class="table-wrap">' + m.group(0) + '</div>'
    body_html = re.sub(r'<table>.*?</table>', table_repl, body_html, flags=re.DOTALL)

    # 4. 核心信号卡片化：<p><strong>N. 标题</strong></p> + <ul>…</ul> → .signal-card
    #    标题前缀支持 "1. " 与 "信号N：" 两种编号；同时兼容历史格式 <h3> 标题。
    def card_title_html(raw_title):
        tm = re.match(r'信号(\d+)\s*[：:]\s*(.*)', raw_title, re.DOTALL)
        if tm:
            return (f'<strong><span class="num">信号{tm.group(1)}：</span>'
                    f'{tm.group(2)}</strong>')
        tm = re.match(r'(\d+\.)\s*(.*)', raw_title, re.DOTALL)
        if tm:
            return (f'<strong><span class="num">{tm.group(1)}</span>'
                    f'{tm.group(2)}</strong>')
        return f'<strong>{raw_title}</strong>'

    def card_lbl_html(ul_html):
        # li 前缀标签高亮（数据支撑 / 产业链含义 / 对持仓含义 …），兼容 **标签** 与裸文本
        return re.sub(
            r'<li>(?:<strong>)?((?:数据支撑|产业链含义|对持仓含义|持仓含义|关键数据|风险提示))(?:</strong>)?[：:]',
            r'<li><span class="lbl">\1</span>：', ul_html)

    def card_wrap(title_html, ul_html):
        return (f'<div class="signal-card"><div class="sc-title">{title_html}</div>'
                f'<ul>{ul_html}</ul></div>')

    def card_repl(m):
        return card_wrap(card_title_html(m.group(1)), card_lbl_html(m.group(2)))
    body_html = re.sub(
        r'<p><strong>((?:信号\d+[：:]|\d+\.)\s*[^<]*?)</strong></p>\s*<ul>(.*?)</ul>',
        card_repl, body_html, flags=re.DOTALL)
    body_html = re.sub(
        r'<h3>((?:信号\d+[：:]|\d+\.)\s*[^<]*?)</h3>\s*<ul>(.*?)</ul>',
        card_repl, body_html, flags=re.DOTALL)

    # 5. 段落式/混合式信号卡片化（早期日报 8/03-8/14 变体）：
    #    信号标题后跟的是 <p>段落（标签段/正文段）或 <hr>，而非 <ul>。
    #    只在「核心信号」h2 区块内处理，避免误伤其他章节。
    def _para_signal_to_card(raw_title, body):
        tm = re.match(r'信号(\d+)\s*[：:]\s*(.*)', raw_title, re.DOTALL)
        if tm:
            num, title = f'信号{tm.group(1)}：', tm.group(2)
        else:
            tm = re.match(r'(\d+\.)\s*(.*)', raw_title, re.DOTALL)
            num = tm.group(1) if tm else ''
            title = tm.group(2) if tm else raw_title
        title_html = f'<strong><span class="num">{num}</span>{title}</strong>'
        # <p><strong>标签：</strong> 内容 → <li><span class="lbl">标签</span>：内容</li>
        # <p>普通正文</p> → <li>正文</li>；<hr> 删除
        def p2li(m2):
            inner = m2.group(1)
            tag = re.match(
                r'<strong>((?:数据支撑|产业链含义|对持仓含义|持仓含义|关键数据|风险提示))[：:]?</strong>',
                inner)
            if tag:
                rest = inner[tag.end():].lstrip('：: \t')
                return f'<li><span class="lbl">{tag.group(1)}</span>：{rest}</li>'
            plain = re.sub(r'<[^>]+>', '', inner).strip()
            if plain:
                return f'<li>{inner}</li>'
            return ''
        body = re.sub(r'<p>(.*?)</p>', p2li, body, flags=re.DOTALL)
        body = re.sub(r'<hr\s*/?>', '', body)
        # 已存在的 <ul><li>（8/07 列表式 li）加标签高亮
        body = card_lbl_html(body)
        return (f'<div class="signal-card"><div class="sc-title">{title_html}</div>'
                f'<ul>{body}</ul></div>')

    def _para_cardify(seg):
        # 第一轮：h3 型标题 + 其后内容（到下一个 h3）
        def h3_card(m):
            return _para_signal_to_card(m.group(1), m.group(2))
        seg = re.sub(
            r'<h3>((?:信号\d+[：:]|\d+\.)\s*[^<]*?)</h3>\s*((?:(?!<h3>).)*?)(?=<h3>|\Z)',
            h3_card, seg, flags=re.DOTALL)
        # 第二轮：p 型标题（标题独立 p，或标题+正文同 p）+ 其后内容
        def p_card(m):
            raw_title = m.group(1)
            tail = m.group(2).strip()      # 标题 p 内残留正文（8/14 变体）
            body = m.group(3)
            if tail:
                body = f'<li>{tail}</li>\n' + body
            return _para_signal_to_card(raw_title, body)
        seg = re.sub(
            r'<p><strong>((?:信号\d+[：:]|\d+\.)\s*[^<]*?)</strong>(.*?)</p>\s*'
            r'((?:(?!<p><strong>(?:信号\d+[：:]|\d+\.)\s*).)*?)(?=<p><strong>(?:信号\d+[：:]|\d+\.)\s*|\Z)',
            p_card, seg, flags=re.DOTALL)
        return seg

    body_html = re.sub(
        r'(<h2[^>]*核心信号[^>]*>.*?</h2>)(.*?)(?=<h2|\Z)',
        lambda m: m.group(1) + _para_cardify(m.group(2)),
        body_html, flags=re.DOTALL)

    return body_html


# ---------------------------------------------------------------------------
# 页面模板
# ---------------------------------------------------------------------------
def render_article(badge, title, date_label, subtitle, body_html,
                   toc=None, prev_html=None, next_html=None,
                   home_href='../index.html', footer_note='',
                   og_desc='', og_url='', og_image=None):
    toc_html = ''
    if toc:
        items = ''.join(
            f'<a href="#{anchor}">{label}</a>'
            for anchor, label in toc
        )
        toc_html = f'<nav class="toc">{items}</nav>'

    prev_a = (f'<a class="nav-arrow" href="{prev_html}">← {prev_html.replace("report_", "").replace(".html", "")}</a>'
              if prev_html else '<span class="nav-arrow disabled">← 无更早</span>')
    next_a = (f'<a class="nav-arrow" href="{next_html}">{next_html.replace("report_", "").replace(".html", "")} →</a>'
              if next_html else '<span class="nav-arrow disabled">无更新 →</span>')

    og_img = og_image or 'https://reports.xiaoyiyi.wang/assets/og-share.jpg'
    page_title = f'{title} | {date_label.split("·")[0].strip()}'

    css = f'''
*,*::before,*::after{{margin:0;padding:0;box-sizing:border-box}}
:root{{
  --bg:#030712;--card-bg:rgba(15,23,42,.72);--card-solid:#0d1117;
  --blue:#60a5fa;--cyan:#22d3ee;--purple:#a78bfa;--gold:#fbbf24;
  --green:#34d399;--red:#f87171;--pink:#f472b6;--yellow:#facc15;--gray:#64748b;
  --text:#f1f5f9;--text-dim:#64748b;--text-mid:#94a3b8;
  --border:rgba(148,163,184,.1);--border-hi:rgba(148,163,184,.22);
  --ease-out-quint:cubic-bezier(.23,1,.32,1);
  --up:#f87171;--down:#4ade80;
}}
html{{scroll-behavior:smooth}}
body{{
  font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','SF Pro Display','Microsoft YaHei',system-ui,sans-serif;
  background:var(--bg);color:var(--text);min-height:100vh;
  overflow-x:hidden;-webkit-font-smoothing:antialiased;-webkit-tap-highlight-color:transparent;
  line-height:1.75;font-size:15px;
}}
/* 背景光晕 */
.bg{{
  position:fixed;inset:0;z-index:0;pointer-events:none;
  background:
    radial-gradient(ellipse at 18% -5%,rgba(96,165,250,.09),transparent 55%),
    radial-gradient(ellipse at 85% 15%,rgba(167,139,250,.07),transparent 50%),
    radial-gradient(ellipse at 50% 110%,rgba(52,211,153,.05),transparent 55%);
}}
/* 扫描线 */
.scan{{
  position:fixed;left:0;width:100%;height:1px;z-index:2;pointer-events:none;
  background:linear-gradient(90deg,transparent,rgba(34,211,238,.35),transparent);
  animation:scanDown 8s linear infinite;
}}
@keyframes scanDown{{0%{{top:-1px;opacity:0}}3%{{opacity:1}}97%{{opacity:1}}100%{{top:100%;opacity:0}}}}
/* 阅读进度条 */
.progress{{
  position:fixed;top:0;left:0;height:2px;width:0;z-index:99;
  background:linear-gradient(90deg,var(--blue),var(--cyan),var(--gold));
  box-shadow:0 0 8px rgba(34,211,238,.5);
}}
/* 页面容器 */
.page{{position:relative;z-index:1;max-width:800px;margin:0 auto;padding:26px 18px 60px}}
/* Hero */
.hero{{text-align:center;padding:8px 0 20px;animation:enterUp .7s var(--ease-out-quint) .05s both}}
.hero-badge{{
  display:inline-flex;align-items:center;gap:6px;padding:4px 14px;border-radius:100px;
  background:rgba(96,165,250,.08);border:1px solid rgba(96,165,250,.18);
  font-size:.62em;color:var(--blue);letter-spacing:.14em;text-transform:uppercase;
}}
.hero-badge .blink{{
  width:6px;height:6px;border-radius:50%;background:var(--green);
  box-shadow:0 0 8px var(--green);animation:pulse 2.5s ease-in-out infinite;
}}
@keyframes pulse{{0%,100%{{opacity:1;transform:scale(1)}}50%{{opacity:.35;transform:scale(.7)}}}}
.hero h1{{
  font-size:clamp(1.45em,5.5vw,2em);font-weight:800;line-height:1.2;
  letter-spacing:-.03em;margin:12px 0 6px;color:#f0f6fc;
  text-shadow:0 0 30px rgba(96,165,250,.4);
}}
.hero .hero-line{{width:130px;height:3px;margin:10px auto 0;border-radius:3px;
  background:linear-gradient(90deg,var(--blue),var(--cyan),var(--purple),var(--pink));}}
.hero .sub{{font-size:.8em;color:var(--text-dim);letter-spacing:.08em;margin-bottom:12px}}
.hero .meta-line{{display:flex;flex-wrap:wrap;gap:8px;justify-content:center}}
.hero .chip{{
  display:inline-flex;align-items:center;gap:5px;padding:4px 12px;border-radius:100px;
  background:var(--card-bg);border:1px solid var(--border);color:var(--text-mid);
  font-size:.72em;font-weight:600;
}}
.hero .chip.hl{{border-color:rgba(240,185,11,.35);color:var(--gold);background:rgba(240,185,11,.07)}}
@keyframes enterUp{{from{{transform:translateY(16px)}}to{{transform:translateY(0)}}}}
/* TOC */
.toc{{
  display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:4px 0 20px;
  animation:enterUp .5s var(--ease-out-quint) .3s both;
}}
.toc a{{
  color:var(--blue);background:var(--card-bg);border:1px solid var(--border);
  padding:5px 14px;border-radius:100px;font-size:.8em;text-decoration:none;
  transition:all .2s ease;
}}
.toc a:hover{{border-color:var(--blue);background:rgba(96,165,250,.1);color:#93c5fd}}
/* 工具栏（返回 + 前后篇） */
.toolbar{{
  display:flex;align-items:center;justify-content:space-between;gap:10px;
  margin-bottom:18px;flex-wrap:wrap;
  animation:enterUp .5s var(--ease-out-quint) .35s both;
}}
.back-link{{
  display:inline-flex;align-items:center;gap:4px;font-size:.78em;color:var(--text-dim);
  text-decoration:none;padding:7px 14px;border-radius:10px;
  background:var(--card-bg);border:1px solid var(--border);transition:all .2s;
}}
.back-link:hover{{color:var(--cyan);border-color:rgba(34,211,238,.4)}}
.nav-arrows{{display:flex;gap:8px}}
.nav-arrow{{
  font-size:.74em;color:var(--text-mid);text-decoration:none;padding:7px 12px;
  border-radius:10px;background:var(--card-bg);border:1px solid var(--border);
  transition:all .2s;
}}
.nav-arrow:hover{{color:var(--blue);border-color:var(--blue)}}
.nav-arrow.disabled{{color:var(--text-dim);opacity:.45;cursor:default}}
/* 正文卡片 */
.content{{
  background:var(--card-bg);border:1px solid var(--border);border-radius:18px;
  padding:26px 28px 30px;
  animation:enterUp .55s var(--ease-out-quint) .42s both;
}}
/* markdown 内容样式 */
.md{{font-size:.95em;line-height:1.85;word-break:break-word;-webkit-text-size-adjust:100%}}
/* ── h2 大标题：金色渐变标题条 ── */
.md h2{{
  margin:44px 0 20px;padding:13px 20px;font-size:1.16em;font-weight:800;
  color:var(--gold);letter-spacing:.04em;
  background:linear-gradient(100deg,rgba(251,191,36,.16),rgba(251,191,36,.05) 55%,rgba(251,191,36,0));
  border:1px solid rgba(251,191,36,.22);border-left:5px solid var(--gold);
  border-radius:14px;box-shadow:0 3px 22px rgba(251,191,36,.07);
  display:flex;align-items:center;gap:10px;position:relative;
}}
.md h2::after{{
  content:'';position:absolute;right:14px;top:50%;transform:translateY(-50%);
  width:64px;height:2px;border-radius:2px;opacity:.7;
  background:linear-gradient(90deg,transparent,rgba(251,191,36,.55));
}}
.md h2 .sec-emoji{{font-size:1.05em;filter:drop-shadow(0 0 6px rgba(251,191,36,.5))}}
/* ── h3 小标题：青色胶囊标签 ── */
.md h3{{
  margin:32px 0 12px;padding:6px 16px;font-size:1.04em;font-weight:800;
  color:#67e8f9;letter-spacing:.03em;display:inline-block;
  background:linear-gradient(135deg,rgba(34,211,238,.16),rgba(34,211,238,.04));
  border:1px solid rgba(34,211,238,.28);border-radius:9px;
  box-shadow:inset 0 0 14px rgba(34,211,238,.05);
}}
/* ── h4 小标题：紫色圆点 ── */
.md h4{{margin:22px 0 8px;font-size:.97em;font-weight:800;color:#c4b5fd;
  display:flex;align-items:center;gap:8px;letter-spacing:.02em}}
.md h4::before{{content:'';width:7px;height:7px;border-radius:50%;
  background:linear-gradient(135deg,var(--purple),var(--pink));box-shadow:0 0 8px rgba(167,139,250,.7)}}
.md p{{margin:12px 0;color:var(--text-mid)}}
.md strong{{color:var(--text);font-weight:700}}
.md em{{color:var(--pink);font-style:normal}}
.md a{{color:var(--blue);text-decoration:none;border-bottom:1px dashed rgba(96,165,250,.4)}}
.md a:hover{{border-bottom-style:solid}}
.md ul,.md ol{{margin:10px 0;padding-left:24px}}
.md li{{margin:6px 0;color:var(--text-mid);line-height:1.8}}
.md ul>li{{list-style:'›  '}}
.md ul>li::marker{{color:var(--cyan)}}
.md ul ul>li{{list-style:'·  ';font-size:.95em}}
.md ul ul>li::marker{{color:var(--text-dim)}}
.md ol>li::marker{{color:var(--gold);font-weight:700}}
.md li>strong{{color:var(--text)}}
.md blockquote{{
  margin:16px 0;padding:13px 18px;border-left:3px solid var(--gold);
  background:rgba(251,191,36,.05);border-radius:0 12px 12px 0;
  font-size:.93em;color:var(--text-mid);
}}
.md blockquote strong{{color:var(--gold)}}
.md hr{{border:none;height:1px;margin:28px 0;
  background:linear-gradient(90deg,transparent,var(--border-hi),transparent)}}
.md code{{
  font-family:'SF Mono',Menlo,Consolas,monospace;font-size:.86em;
  padding:2px 7px;border-radius:6px;background:rgba(96,165,250,.08);color:var(--blue);
}}
.md pre{{
  background:var(--card-solid);border:1px solid var(--border);border-radius:12px;
  padding:14px 16px;overflow-x:auto;margin:14px 0;
}}
.md pre code{{background:none;padding:0;color:var(--text)}}
.table-wrap{{overflow-x:auto;margin:18px 0;border-radius:14px;-webkit-overflow-scrolling:touch;
  box-shadow:0 3px 20px rgba(0,0,0,.22)}}
.md table{{
  width:100%;border-collapse:separate;border-spacing:0;font-size:.86em;
  border:1px solid var(--border-hi);border-radius:14px;overflow:hidden;
}}
.md thead{{position:relative}}
.md th{{
  background:linear-gradient(135deg,rgba(30,64,175,.55),rgba(8,74,103,.55));
  color:#bae6fd;font-weight:800;padding:12px 15px;text-align:left;
  white-space:nowrap;border-bottom:2px solid rgba(34,211,238,.28);
  letter-spacing:.03em;font-size:.95em;
}}
.md td{{padding:10px 15px;border-top:1px solid var(--border);color:var(--text-mid);
  vertical-align:top;line-height:1.72}}
.md tr:nth-child(even) td{{background:rgba(148,163,184,.05)}}
.md tr:hover td{{background:rgba(96,165,250,.07)}}
.md tbody tr:first-child td{{border-top:none}}
.md td:first-child{{color:#e2e8f0;font-weight:700}}
/* ── 信号卡片（核心信号章节） ── */
.signal-card{{
  margin:20px 0;padding:18px 22px 8px;border-radius:16px;
  background:linear-gradient(180deg,rgba(96,165,250,.07),rgba(15,23,42,.3));
  border:1px solid var(--border-hi);border-left:4px solid var(--blue);
  transition:border-color .25s ease,box-shadow .25s ease;
}}
.signal-card:hover{{border-left-color:var(--cyan);border-color:rgba(96,165,250,.4);
  box-shadow:0 4px 24px rgba(96,165,250,.08)}}
.signal-card .sc-title{{
  font-size:1.03em;font-weight:800;color:#e0f2fe;line-height:1.6;
  padding-bottom:10px;margin-bottom:6px;border-bottom:1px dashed var(--border-hi);
  display:block;
}}
.signal-card .sc-title .num{{
  color:var(--gold);font-weight:900;margin-right:8px;font-size:1.05em;
  text-shadow:0 0 10px rgba(251,191,36,.4);
}}
.signal-card ul{{margin:6px 0 10px !important;padding-left:0 !important;list-style:none !important}}
.signal-card li{{
  position:relative;padding:5px 0 5px 20px;margin:3px 0 !important;
  color:var(--text-mid);line-height:1.78;
}}
.signal-card li::before{{
  content:'';position:absolute;left:2px;top:15px;width:7px;height:7px;border-radius:2px;
  background:linear-gradient(135deg,var(--cyan),var(--blue));
  box-shadow:0 0 6px rgba(34,211,238,.5);
}}
.signal-card li .lbl{{
  color:var(--cyan);font-weight:800;font-size:.93em;margin-right:2px;
  text-shadow:0 0 8px rgba(34,211,238,.25);
}}
/* Footer */
.footer{{
  text-align:center;margin-top:26px;padding-top:18px;
  border-top:1px solid var(--border);font-size:.7em;color:var(--text-dim);
  line-height:2;animation:enterUp .5s var(--ease-out-quint) .6s both;
}}
.footer .hl{{color:var(--gold)}}
.footer .lotus{{color:var(--pink)}}
.footer .warn{{color:var(--text-dim)}}
/* 移动端 */
@media (max-width:600px){{
  .page{{padding:18px 12px 44px}}
  .content{{padding:18px 16px 22px;border-radius:14px}}
  .md{{font-size:.9em}}
  .md h2{{font-size:1em;margin:32px 0 14px;padding:11px 14px}}
  .md h2::after{{display:none}}
  .md h3{{font-size:.98em;padding:5px 12px}}
  .md table{{font-size:.78em}}
  .md th,.md td{{padding:8px 10px}}
  .signal-card{{padding:14px 16px 6px}}
  .signal-card .sc-title{{font-size:.98em}}
  .toc a{{padding:4px 10px;font-size:.74em}}
  .toolbar{{gap:6px}}
}}
@media (prefers-reduced-motion:reduce){{
  *,*::before,*::after{{animation-duration:.01ms !important;transition-duration:.01ms !important}}
  .scan,.progress{{display:none}}
}}
'''

    js = '''
<script>
(function(){
  // 阅读进度条
  var bar = document.getElementById('progressBar');
  function onScroll(){
    var h = document.documentElement;
    var max = h.scrollHeight - h.clientHeight;
    var p = max > 0 ? (h.scrollTop || document.body.scrollTop) / max : 0;
    bar.style.width = (p * 100).toFixed(2) + '%';
  }
  document.addEventListener('scroll', onScroll, {passive:true});
  onScroll();
  // 表格横向滚动（兜底，若渲染时未包裹）
  document.querySelectorAll('.content table').forEach(function(t){
    if (!t.parentNode.classList.contains('table-wrap')) {
      var w = document.createElement('div');
      w.className = 'table-wrap';
      t.parentNode.insertBefore(w, t);
      w.appendChild(t);
    }
  });
})();
</script>
'''

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{page_title}</title>
<meta property="og:type" content="article">
<meta property="og:site_name" content="华尔街之鹰">
<meta property="og:title" content="{page_title}">
<meta property="og:description" content="{og_desc}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="600">
<meta property="og:image:height" content="600">
<meta property="og:url" content="{og_url}">
<meta itemprop="name" content="{page_title}">
<meta itemprop="description" content="{og_desc}">
<meta itemprop="image" content="{og_img}">
<meta name="twitter:card" content="summary_large_image">
<style>{css}</style>
</head>
<body>
<div class="bg"></div>
<div class="scan"></div>
<div class="progress" id="progressBar"></div>

<div class="page">

  <header class="hero">
    <div class="hero-badge"><span class="blink"></span><span>{badge}</span></div>
    <h1><span class="g">{title}</span></h1>
    <div class="sub">{subtitle}</div>
    <div class="hero-line"></div>
    <div class="meta-line">
      <span class="chip hl">📅 {date_label}</span>
    </div>
  </header>

  {toc_html}

  <div class="toolbar">
    <a class="back-link" href="{home_href}">← 返回列表</a>
    <div class="nav-arrows">{prev_a}{next_a}</div>
  </div>

  <article class="content">
    {body_html}
  </article>

  <div class="toolbar" style="margin-top:18px;justify-content:center;animation:none;opacity:1">
    <a class="back-link" href="{home_href}">← 返回列表</a>
  </div>

  <footer class="footer">
    <p><span class="hl">🦅 华尔街之鹰</span> · 由 <span class="lotus">🪷 小荷</span> 自动整理</p>
    <p>{footer_note}</p>
    <p class="warn">⚠️ 本报告仅供信息参考，不构成任何投资建议。市场有风险，投资需谨慎。</p>
  </footer>

</div>
{js}
</body>
</html>'''
    return html
