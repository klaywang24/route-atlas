#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成三家族各自的 index.html 与站首页 index.html。

    python3 tools/build_index.py

读 regions/*.py 的 META（title/h1/kicker/family/OUT），不碰航线数据。
壳与区域页同源（tools/shell/），调色板同样由 tools/build_theme.py 注入 —— 所以顺序：本脚本 → build_theme.py。
"""
import io, os, re, sys, importlib.util
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_region_page import shell_parts, EXTRA_CSS, FAMILIES, fam_bar, HERE

# 站首页世界流向总图：每个数据模块＝出发家族 → 目的地区域；镜像页反向再画一条（班次每方向相同）
DEST = {"usa": "美国", "us_cn": "中国", "europe": "欧洲", "eu_cn": "中国", "asia": "亚洲", "canada": "加拿大", "africa": "非洲",
        "oceania": "澳新", "us_eu": "欧洲", "eu_us": "美国", "us_asia": "亚洲", "us_ca": "加拿大", "us_mx": "墨西哥·加勒比",
        "us_sa": "南美", "us_oc": "澳新", "eu_asia": "亚洲", "eu_africa": "非洲"}
ORIGIN = {"中国出发": "中国", "美国出发": "美国", "欧洲出发": "欧洲"}
FLAG = {"中国": "🇨🇳", "美国": "🇺🇸", "欧洲": "🇪🇺", "亚洲": "🌏", "加拿大": "🇨🇦", "非洲": "🌍", "澳新": "🇦🇺", "南美": "🌎", "墨西哥·加勒比": "🇲🇽"}
FCOL = {"中国出发": "var(--accent)", "美国出发": "var(--teal,#00A86B)", "欧洲出发": "var(--ink-soft,#5B5347)"}

def world_flow(pages):
    """返回 (html, script)：出发家族 → 目的地区域，线粗＝该页直飞班次合计。"""
    import json
    o_nodes, d_nodes, edges = {}, {}, []
    for p in pages:
        if not p.get("dest"): continue
        o = ORIGIN[p["family"]]; d = p["dest"]
        o_nodes.setdefault(o, 0); o_nodes[o] += p["wk"]; d_nodes.setdefault(d, 0); d_nodes[d] += p["wk"]
        edges.append(dict(a="o:" + o, b="d:" + d, w=max(.6, p["wk"] / 100.0), width=max(1.2, min(10, p["wk"] / 120.0 + 1)),
                          cat=p["family"], color=FCOL[p["family"]], opacity=.55,
                          tip="<b>%s → %s</b><br>%s<br>直飞 %d 条 · 合计 %d 班/周（每方向）%s" % (o, d, strip_tags(p["meta"]["h1"]), p["n_direct"], p["wk"], "<br>镜像页，数据同源" if p["mirror"] else ""),
                          href="%s/%s" % (p["family"], p["out"])))
    nodes = [dict(id="o:" + k, col=0, label="%s %s" % (FLAG.get(k, ""), k), sub="%d 班/周" % v, group="— 出发 —") for k, v in sorted(o_nodes.items(), key=lambda x: -x[1])]
    nodes += [dict(id="d:" + k, col=1, label="%s %s" % (FLAG.get(k, ""), k), sub="%d 班/周" % v, group="— 目的地 —") for k, v in sorted(d_nodes.items(), key=lambda x: -x[1])]
    spec = dict(id="wf", W=1100, top=44, bottom=20, isolate="touch", particleDiv=7,
                cols=[dict(label="出发", x=[40, 244], kind="card", h=40, gap=6, groupGap=16),
                      dict(label="目的地（按班次排）", x=[866, 1064], kind="card", h=36, gap=4, groupGap=16)],
                legend=[dict(k=f, label=f, color=FCOL[f]) for f, _ in FAMILIES if any(e["cat"] == f for e in edges)],
                controls=[dict(type="legend", label="出发家族"), dict(type="reset")], nodes=nodes, edges=edges)
    js = ("<script>(function(){var root=document.getElementById('flow');if(!root||!window.FlowViz)return;var S=%s;"
          "S.note=function(st){return '亮着 <b>'+st.lit.length+'</b> 条走廊。<b>线粗＝该页直飞班次合计</b>（每方向/周，只算已核的数）。点节点只看它，具体页在下面的卡片。渲染＝FlowViz v'+FlowViz.version+'。';};"
          "S.edges.forEach(function(e){delete e.href;});"
          "FlowViz.embed(root,S);})();</script>") % json.dumps(spec, ensure_ascii=False)
    return '<div id="flow"></div>', js

def load_all():
    out = []
    rd = os.path.join(HERE, "regions")
    if rd not in sys.path: sys.path.insert(0, rd)       # 镜像模块 from _mirror import …
    for f in sorted(os.listdir(os.path.join(HERE, "regions"))):
        if not f.endswith(".py") or f.startswith("_"): continue
        sp = importlib.util.spec_from_file_location(f[:-3], os.path.join(HERE, "regions", f))
        m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
        src = m
        if getattr(m, "MIRROR_OF", None):
            sp2 = importlib.util.spec_from_file_location(m.MIRROR_OF, os.path.join(HERE, "regions", m.MIRROR_OF + ".py"))
            src = importlib.util.module_from_spec(sp2); sp2.loader.exec_module(src)
        routes = getattr(m, "ROUTES", None) or getattr(src, "ROUTES", [])
        oc = getattr(m, "OUT_CAT", None) or getattr(src, "OUT_CAT", "已退出")
        n_all = len(routes); n_out = sum(1 for r in routes if r[6] == oc)
        out.append(dict(slug=f[:-3], family=getattr(m, "FAMILY", "中国出发"), out=m.OUT, meta=m.META,
                        n=n_all, n_direct=n_all - n_out, mirror=getattr(m, "MIRROR_OF", None),
                        dest=getattr(m, "DEST", None) or getattr(src, "DEST", None) or DEST.get(f[:-3]),
                        origin_region=getattr(m, "ORIGIN", None) or getattr(src, "ORIGIN", None) or ORIGIN.get(getattr(src, "FAMILY", "中国出发")),
                        wk=sum(r[4] for r in routes if r[6] != oc)))
    return out

def strip_tags(t): return re.sub(r"<[^>]+>", "", t)

def page(title, brand, brand_zh, h1, sub, kicker, body, family=None, toc=None, depth=1):
    head, top, tocjs, star, dark = shell_parts()
    toc_html = "".join('\n  <a class="toc-item" href="#%s"><span class="tn">%s</span>%s</a>' % t for t in (toc or []))
    fam = fam_bar(family) if family else ""
    if not family:  # 站首页：家族条全部链到子目录
        fam = '<nav class="fam">' + '<span class="sep">·</span>'.join(
            '<a href="%s/index.html">%s %s</a>' % (n, fl, n) for n, fl in FAMILIES) + '</nav>'
    else:
        fam = fam.replace('href="../index.html"', 'href="../index.html"')
    return ("<!DOCTYPE html>\n<html lang=\"zh-CN\">\n<head>\n<meta charset=\"UTF-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n<title>%s</title>\n"
            "<!-- THEME:START --><!-- THEME:END -->\n" % title + head + "\n" + EXTRA_CSS + top
            + '<aside class="toc-sidebar" id="toc">\n  <div class="toc-brand">%s<span class="dot">.</span></div>\n  <div class="toc-zh">%s</div>%s\n</aside>\n'
              '<div class="toc-backdrop" id="tocBack"></div>\n\n<div class="wrap">\n%s<h1>%s</h1>\n<div class="sub">%s</div>\n<div class="kicker">%s</div>\n'
              % (brand, brand_zh, toc_html, fam, h1, sub, kicker)
            + body + '\n<footer>中国出发 · 美国出发 · 欧洲出发 三家族同一设计系统 · 班次按每方向每周 · 逐线票价一律未核 · 换季重核</footer>\n</div>\n'
            + "\n<script>\n" + dark + "\n" + tocjs + "\n</script>\n" + star + "\n</body>\n</html>\n")

def card(p):
    m = p["meta"]
    one = strip_tags(m.get("kicker", "")).split("。")[0] + "。"
    return ('<a class="pcard" href="%s"><div class="pc-t">%s</div><div class="pc-s">%s</div>'
            '<div class="pc-n">%d 条线 · 直飞 %d%s</div></a>'
            % (p["out"], strip_tags(m["h1"]), one, p["n"], p["n_direct"], "　·　镜像页" if p["mirror"] else ""))

CARD_CSS = """<style>
.pgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px;margin:14px 0 26px}
.pcard{display:block;padding:16px 18px;border:1px solid var(--rule);border-radius:12px;background:var(--bg-card);text-decoration:none;color:var(--ink);transition:.14s}
.pcard:hover{border-color:var(--accent);transform:translateY(-1px)}
.pc-t{font-family:Georgia,'Songti SC',serif;font-size:18px;font-weight:600;margin-bottom:6px}
.pc-s{font-size:13.5px;color:var(--ink-soft);line-height:1.7;margin-bottom:8px}
.pc-n{font-size:12px;color:var(--muted);font-family:ui-monospace,Menlo,monospace}
.fcard{padding:18px 20px;border:1px solid var(--rule);border-radius:12px;background:var(--bg-card);margin:12px 0}
.fcard h3{margin:0 0 6px;font-size:18px}
.fcard .fc-n{font-size:12px;color:var(--muted);font-family:ui-monospace,Menlo,monospace;margin-bottom:8px}
</style>
"""

def main():
    pages = load_all()
    # 各家族 index
    for name, flag in FAMILIES:
        ps = [p for p in pages if p["family"] == name]
        d = os.path.join(HERE, name); os.makedirs(d, exist_ok=True)
        if ps:
            body = CARD_CSS + '<h2 id="s1">%s 出发 · 全部页面<span class="zh">%d 页</span></h2>\n<div class="pgrid">%s</div>' % (flag, len(ps), "".join(card(p) for p in ps))
        else:
            body = CARD_CSS + '<h2 id="s1">%s 出发<span class="zh">尚未建页</span></h2><div class="kicker">研究中，等数据回来再灌。</div>' % flag
        html = page("%s · 航线图志" % name, "Atlas", name, "%s <em>%s</em>" % (flag, name), "ROUTE ATLAS · %s · 2026-09" % name,
                    "按目的地分页，每页一张流向图 ＋ 逐线表 ＋ 政策与航权背景。<b>班次一律每方向/周，逐线票价一律未核。</b>",
                    body, family=name, toc=[("s1", "I", "全部页面")])
        io.open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(html)
        print("✅ %s/index.html  %d 页" % (name, len(ps)))
    # 站首页
    secs = []
    for name, flag in FAMILIES:
        ps = [p for p in pages if p["family"] == name]
        secs.append('<div class="fcard"><h3><a href="%s/index.html">%s %s</a></h3><div class="fc-n">%d 页 · %d 条线</div>%s</div>'
                    % (name, flag, name, len(ps), sum(p["n"] for p in ps),
                       ('<div class="pgrid">%s</div>' % "".join(card(p).replace('href="', 'href="%s/' % name) for p in ps)) if ps else '<div class="kicker">研究中。</div>'))
    flow_html, flow_js = world_flow(pages)
    body = (CARD_CSS + '<h2 id="s0">世界流向总图<span class="zh">三个出发地 → 七个目的地区域</span></h2>\n'
            '<div class="kicker"><b>红＝中国出发，绿＝美国出发，灰＝欧洲出发。</b>线粗＝该页已核直飞班次合计，点节点只看它。欧洲出发目前是镜像数据，与对面那条同源。</div>\n'
            + flow_html + '\n<h2 id="s1">三个出发地<span class="zh">互相倒流</span></h2>\n' + "\n".join(secs) + "\n" + flow_js)
    html = page("航线图志 · Route Atlas", "Atlas", "航线图志", "航线<em>图志</em>", "ROUTE ATLAS · 中国 · 美国 · 欧洲 出发 · 2026-09",
                "按<b>出发地</b>分三个家族，同一批航线在不同家族里是<b>同一份数据、不同视角</b>：中欧和欧中共用一份数据，只换叙事与流向图默认方向。"
                "每页一张流向图 ＋ 逐线表 ＋ 政策与航权背景，来源分级，未核项单独列。",
                body, family=None, toc=[("s0", "0", "世界流向总图"), ("s1", "I", "三个出发地")])
    io.open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(html)
    print("✅ index.html")

if __name__ == "__main__":
    main()
