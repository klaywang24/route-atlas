#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""区域航线页生成器（2026-09-10 建）。

一处判据只能有一个实现：所有区域页的**壳、CSS、流向图适配器**都在这里，
各页只提供数据（regions/*.py），每个数据模块用 FAMILY 声明自己属于哪个出发地目录。

    python3 tools/build_region_page.py            生成全部
    python3 tools/build_region_page.py europe     只生成一张

壳存在 tools/shell/。调色板由 tools/build_theme.py 注入，
流向图运行时由 tools/inject_flowviz.py 注入，两者都不在本文件里写死。
"""
import io, os, re, sys, importlib.util

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHELL = os.path.join(HERE, "tools", "shell")

def shell_parts():
    """壳 5 件（FOUC 脚本+CSS、body 开头、目录 spy、星空滚动、夜间切换），
    2026-09-10 从信用卡仓的大陆差旅选店器.html 抽出，存在 tools/shell/，本仓不再依赖那个私有仓。"""
    R = lambda n: io.open(os.path.join(SHELL, n), encoding="utf-8").read()
    return R("head.html"), R("top.html"), R("toc.js"), R("star.js"), R("dark.js")

FAMILIES = [("中国出发", "🇨🇳"), ("美国出发", "🇺🇸"), ("欧洲出发", "🇪🇺")]

def fam_bar(current):
    """顶栏家族切换：当前家族高亮，其余链到各自 index.html；最右链到站首页。"""
    items = []
    for name, flag in FAMILIES:
        cls = ' class="on"' if name == current else ""
        href = "index.html" if name == current else "../%s/index.html" % name
        items.append('<a%s href="%s">%s %s</a>' % (cls, href, flag, name))
    return '<nav class="fam">' + '<span class="sep">·</span>'.join(items) + '<a class="idx" href="../index.html">全站首页 ↗</a></nav>'

EXTRA_CSS = """<style>
/* 区域航线页专用（三张共用，生成器唯一实现） */
.mono{font-family:ui-monospace,Menlo,monospace;font-size:12.5px}
td.num,th.num{text-align:right;font-family:ui-monospace,Menlo,monospace;white-space:nowrap}
.mini{font-size:11.5px;color:var(--muted);display:block;line-height:1.5}
.badge{display:inline-block;font-size:11px;font-weight:700;border-radius:5px;padding:1px 7px;white-space:nowrap}
.b-ok{background:var(--moss-soft);color:var(--moss);border:1px solid var(--moss)}
.b-warn{background:var(--gold-soft);color:var(--gold);border:1px solid var(--gold)}
.b-err{background:var(--accent-soft);color:var(--accent);border:1px solid var(--accent)}
.b-neu{background:var(--bg-deep);color:var(--muted);border:1px solid var(--rule)}
tr.gone td{opacity:.62}
tr.gone td:first-child{opacity:1}
.tblwrap{overflow-x:auto;margin:12px 0}
table.wide{min-width:940px}
.cn{font-weight:600;white-space:nowrap}
ul.clean{list-style:none;margin:12px 0}
ul.clean li{position:relative;padding-left:15px;margin:8px 0;font-size:14.5px;line-height:1.85}
ul.clean li:before{content:"";position:absolute;left:0;top:.72em;width:5px;height:5px;border-radius:50%;background:var(--rule)}
.callout.okcall{background:var(--moss-soft);border-left-color:var(--moss)}
.callout.okcall b{color:var(--moss)}
.callout.warncall{background:var(--gold-soft);border-left-color:var(--gold)}
.callout.warncall b{color:var(--gold)}
#flow{margin:14px 0 6px}
/* 家族切换条（三家族互相倒流的第一层） */
.fam{display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin:0 0 18px;font-size:13px}
.fam a{display:inline-flex;align-items:center;gap:6px;padding:5px 12px;border-radius:999px;border:1px solid var(--rule);
  background:var(--bg-card);color:var(--ink-soft);text-decoration:none;transition:.14s}
.fam a:hover{border-color:var(--accent);color:var(--accent)}
.fam a.on{background:var(--accent);border-color:var(--accent);color:#fff;font-weight:700}
.fam .sep{color:var(--muted-soft);margin:0 2px}
.fam .idx{margin-left:auto;color:var(--muted);font-size:12px}
.mirror{display:inline-block;margin:0 0 6px 2px;font-size:13px;color:var(--accent);text-decoration:none;border-bottom:1px dashed var(--accent)}
.mirror:hover{border-bottom-style:solid}
</style>
"""

# 流向图适配器：读表格 DOM，不另抄一份数据（与航司页同规矩）
ADAPTER = """<script>
/* 流向图适配器：解析本页所有 tr.tp（data-cn / data-fo / data-direct / data-wk / data-cat），渲染走 FlowViz。
   数据只有表格一份，改表即改图。 */
(function(){
  var root=document.getElementById('flow'); if(!root||!window.FlowViz) return;
  var CAT=__CAT__;
  var FOFLAG=__FOFLAG__;
  var OFLAG='__OFLAG__', OGRP='__OGRP__', DGRP='__DGRP__';
  function txt(td){ return (td.textContent||'').replace(/\\s+/g,' ').trim(); }
  function num(t){ var m=String(t).match(/\\d[\\d,]*/); return m?+m[0].replace(/,/g,''):0; }
  var rows=[];
  document.querySelectorAll('tr.tp').forEach(function(tr){
    var td=tr.querySelectorAll('td'); if(td.length<3) return;
    var cn=tr.getAttribute('data-cn'), fo=tr.getAttribute('data-fo'); if(!cn||!fo) return;
    rows.push({cn:cn,fo:fo,direct:tr.getAttribute('data-direct')==='1',
      wk:+(tr.getAttribute('data-wk')||0), cat:tr.getAttribute('data-cat')||'其他', grp:tr.getAttribute('data-grp')||'',
      car:txt(td[1]),fq:txt(td[2]),dur:txt(td[3]||''),note:tr.getAttribute('data-note')||''});
  });
  if(!rows.length) return;
  var dir='both', grp='';
  var GRPS=[]; rows.forEach(function(r){ if(r.grp&&GRPS.indexOf(r.grp)<0) GRPS.push(r.grp); });
  function tip(r,d){ return '<b>'+(d==='out'?r.cn+' → '+r.fo:r.fo+' → '+r.cn)+'</b>'+
    (r.direct?'':'🔴 已退出 · ')+r.cat+(r.wk?' · '+r.wk+' 班/周（每方向）':'')+'<br>'+r.car+' · '+r.fq+
    (r.dur&&r.dur!=='未核'?' · '+r.dur:'')+(r.note?'<br>'+r.note:''); }
  function build(){
    var legs=[];
    rows.filter(function(r){ return !grp||r.grp===grp; }).forEach(function(r){
      if(dir!=='in') legs.push({o:r.cn,d:r.fo,r:r,side:'out'});
      if(dir!=='out') legs.push({o:r.fo,d:r.cn,r:r,side:'in'});
    });
    var O=[],D=[];
    legs.forEach(function(l){ if(O.indexOf(l.o)<0)O.push(l.o); if(D.indexOf(l.d)<0)D.push(l.d); });
    var isCN=function(x){ return rows.some(function(r){return r.cn===x;}); };
    /* 先按国别分组（中国城市在前），组内再按航线数降序 —— 否则分组标签会来回跳 */
    var srt=function(arr,k){ return function(a,b){ var ca=isCN(a),cb=isCN(b); if(ca!==cb) return ca?-1:1;
      return arr.filter(function(l){return l[k]===b;}).length-arr.filter(function(l){return l[k]===a;}).length; }; };
    O.sort(srt(legs,'o')); D.sort(srt(legs,'d'));
    var nodes=[],edges=[];
    O.forEach(function(o){ var ls=legs.filter(function(l){return l.o===o;}), dn=ls.filter(function(l){return l.r.direct;}).length;
      nodes.push({id:'o:'+o,col:0,label:(isCN(o)?OFLAG+' ':(FOFLAG[o]||'')+' ')+o,sub:ls.length+' 条（直飞 '+dn+'）',group:isCN(o)?'— '+OGRP+'出发 —':'— '+DGRP+'出发 —'}); });
    D.forEach(function(d){ var ls=legs.filter(function(l){return l.d===d;});
      var w=ls.reduce(function(a,l){return a+(l.r.wk||0);},0);
      nodes.push({id:'d:'+d,col:1,label:(isCN(d)?OFLAG+' ':(FOFLAG[d]||'')+' ')+d,sub:ls.length+' 条进港'+(w?' · '+w+' 班/周':''),group:isCN(d)?'— 飞往'+OGRP+' —':'— '+DGRP+' —'}); });
    legs.forEach(function(l){ var w=Math.max(.6,(l.r.wk||1)/7);
      edges.push({a:'o:'+l.o,b:'d:'+l.d,w:w,width:Math.max(1,Math.min(9,.9*w+1)),cat:l.r.cat,
        color:CAT[l.r.cat]||'var(--muted)',dash:!l.r.direct,opacity:l.r.direct?.5:.32,tip:tip(l.r,l.side)}); });
    return {id:'rf',W:1100,top:44,bottom:20,isolate:'touch',particleDiv:7,
      cols:[{label:'出发',x:[40,244],kind:'card',h:38,gap:4,groupGap:16},
            {label:'目的地（按航线数排）',x:[866,1064],kind:'card',h:34,gap:3,groupGap:16}],
      legend:Object.keys(CAT).map(function(k){return {k:k,label:k,color:CAT[k]};}),
      controls:[{type:'pills',label:'方向',options:[{v:'out',label:OGRP+'→'+DGRP},{v:'in',label:DGRP+'→'+OGRP},{v:'both',label:'双向'}],value:dir,
                 onChange:function(v){dir=v;h.update(build());}}]
        .concat(GRPS.length>1?[{type:'pills',label:'目的地',options:[{v:'',label:'全部'}].concat(GRPS.map(function(g){return {v:g,label:g};})),value:grp,
                 onChange:function(v){grp=v;h.update(build());}}]:[])
        .concat([{type:'legend',label:'承运方'},{type:'reset',onReset:function(){dir='both';grp='';h.update(build());}}]),
      nodes:nodes,edges:edges,
      note:function(st){ var nd=st.lit.filter(function(e){return !e.dash;}).length;
        return '亮着 <b>'+st.lit.length+'</b> 条（直飞 '+nd+'）'+(st.sel?'，只看 <b>'+st.sel.slice(2)+'</b>':'')+
        '。<b>线粗＝每周班次</b>，虚线＝需中转。班次按每方向计，两个方向相同。渲染＝FlowViz v'+FlowViz.version+'。'; }};
  }
  var h=FlowViz.embed(root,build()); window.rfFlow=h;
})();
</script>"""

def table(rows, cols):
    """rows: list of dict(cn,fo,direct,wk,cat,cells[list],cls)"""
    th = "".join('<th%s>%s</th>' % (' class="num"' if c.get('num') else '', c['t']) for c in cols)
    out = ['<div class="tblwrap"><table class="wide"><thead><tr>%s</tr></thead><tbody>' % th]
    for r in rows:
        attrs = ' class="tp%s" data-cn="%s" data-fo="%s" data-direct="%d" data-wk="%s" data-cat="%s"' % (
            (" " + r["cls"]) if r.get("cls") else "", r["cn"], r["fo"], 1 if r.get("direct") else 0,
            r.get("wk", 0), r.get("cat", "其他"))
        if r.get("note"): attrs += ' data-note="%s"' % r["note"].replace('"', '&quot;')
        if r.get("grp"): attrs += ' data-grp="%s"' % r["grp"]
        tds = "".join('<td%s>%s</td>' % (' class="num"' if cols[i].get('num') else (' class="cn"' if i == 0 else ''), c)
                      for i, c in enumerate(r["cells"]))
        out.append("<tr%s>%s</tr>" % (attrs, tds))
    out.append("</tbody></table></div>")
    return "\n".join(out)

def build(spec, outname):
    head, top, toc, star, dark = shell_parts()
    toc_items = "".join(
        '\n  <a class="toc-item" href="#%s"><span class="tn">%s</span>%s</a>' % (s["id"], s["n"], s["nav"])
        for s in spec["sections"])
    body = []
    for s in spec["sections"]:
        body.append('\n<h2 id="%s">%s<span class="zh">%s</span></h2>' % (s["id"], s["h"], s.get("zh", "")))
        if s.get("kick"): body.append('<div class="kicker">%s</div>' % s["kick"])
        body.append(s["html"])
    adapter = (ADAPTER.replace("__CAT__", spec["cat_js"]).replace("__FOFLAG__", spec["flag_js"])
               .replace("__OFLAG__", spec.get("origin_flag", "🇨🇳")).replace("__OGRP__", spec.get("origin_label", "中国"))
               .replace("__DGRP__", spec.get("dest_label", "境外"))
               .replace("var dir='both', grp='';", "var dir='%s', grp='';" % spec.get("default_dir", "both")))
    page = ("<!DOCTYPE html>\n<html lang=\"zh-CN\">\n<head>\n<meta charset=\"UTF-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
            "<title>%s</title>\n<!-- THEME:START --><!-- THEME:END -->\n" % spec["title"]
            + head + "\n" + EXTRA_CSS + top
            + '<aside class="toc-sidebar" id="toc">\n  <div class="toc-brand">%s<span class="dot">.</span></div>\n'
              '  <div class="toc-zh">%s</div>%s\n</aside>\n<div class="toc-backdrop" id="tocBack"></div>\n\n'
              '<div class="wrap">\n%s<h1>%s</h1>\n%s<div class="sub">%s</div>\n<div class="kicker">%s</div>\n'
              % (spec["brand"], spec["brand_zh"], toc_items, fam_bar(spec.get("family", "中国出发")), spec["h1"],
                 ('<a class="mirror" href="%s">换个方向看 · %s ↗</a>\n' % (spec["mirror"], spec.get("mirror_label", "镜像页"))) if spec.get("mirror") else "",
                 spec["sub"], spec["kicker"])
            + "\n".join(body)
            + '\n<footer>%s</footer>\n</div>\n' % spec["footer"]
            + "\n<script>\n" + dark + "\n" + toc + "\n</script>\n" + star + "\n" + adapter + "\n</body>\n</html>\n")
    fam = spec.get("family", "")
    os.makedirs(os.path.join(HERE, fam), exist_ok=True)
    p = os.path.join(HERE, fam, outname)
    # 🔴 自检：渲染行数 == 数据行数。多＝同一航线进了两张表（流向图会重复计数），少＝有航线没被任何 section 收进去。
    n_html = page.count('<tr class="tp')
    n_data = len(spec.get("_routes", []))
    if n_data and n_html != n_data:
        raise SystemExit("⛔ %s/%s 渲染 %d 行，数据 %d 行 —— %s" % (fam, outname, n_html, n_data,
                         "有航线重复进表" if n_html > n_data else "有航线没进任何表"))
    io.open(p, "w", encoding="utf-8").write(page)
    print("✅ %s/%s  %d KB" % (fam, outname, len(page.encode()) // 1024))
    return p

def rows_of(routes, only=None, cat=None, skip=None, out_cat="已退出", groups=None):
    """ROUTES 元组 → table() 需要的 dict。
    only=境外城市集合（None＝不限）；cat=只取该类别；skip=排除该类别。
    🔴 同一条航线只能出现在一张表里，否则流向图会重复计数（适配器读全页 tr.tp）。"""
    out = []
    for cn, fo, car, fq, wk, dur, cat_, note, src in routes:
        if only and fo not in only: continue
        if cat and cat_ != cat: continue
        if skip and cat_ == skip: continue
        out.append(dict(cn=cn, fo=fo, direct=(cat_ != out_cat), wk=wk, cat=cat_, note=note, grp=(groups or {}).get(fo, ""),
                        cls="gone" if cat_ == out_cat else "",
                        cells=["%s ⇄ %s" % (cn, fo), car, fq, dur, note, '<span class="mini">%s</span>' % src]))
    return out

COLS = [{"t": "城市对"}, {"t": "承运人 ＋ 航班号"}, {"t": "班次/周（每方向）"}, {"t": "时长"}, {"t": "备注"}, {"t": "来源"}]

def load(slug):
    rd = os.path.join(HERE, "regions")
    if rd not in sys.path: sys.path.insert(0, rd)       # 镜像模块 from _mirror import …
    p = os.path.join(rd, slug + ".py")
    sp = importlib.util.spec_from_file_location(slug, p)
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    return m

if __name__ == "__main__":
    slugs = sys.argv[1:] or sorted(f[:-3] for f in os.listdir(os.path.join(HERE, "regions")) if f.endswith(".py") and not f.startswith("_"))
    for s in slugs:
        m = load(s)
        if getattr(m, "MIRROR_OF", None):            # 镜像页：数据借源模块，只换视角
            src = load(m.MIRROR_OF)
            for k in ("ROUTES", "GROUPS", "OUT_CAT"):
                if not hasattr(m, k) and hasattr(src, k): setattr(m, k, getattr(src, k))
        spec = m.META; spec["family"] = getattr(m, "FAMILY", "中国出发"); spec["_routes"] = getattr(m, "ROUTES", [])
        oc = getattr(m, "OUT_CAT", "已退出")
        gm = getattr(m, "GROUPS", None)
        bound = lambda routes, only=None, cat=None, skip=None: rows_of(routes, only, cat, skip, out_cat=oc, groups=gm)
        spec["sections"] = m.sections(bound, table, COLS)
        build(spec, m.OUT)
