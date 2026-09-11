# -*- coding: utf-8 -*-
"""镜像页公用：加载源模块、按境外城市汇总「你在哪，能飞哪」表。改数据改源模块，这里只管视角。
承运人列从「承运人＋航班号」栏抽：先去括号（机型/机场）、再去航班号（CA937/938、3U3827）、再去两字代码，剩下按 · ＋ 、 切。
判据＝汇总表里不该出现任何数字；出现了就是正则漏了一种写法。"""
import importlib.util, os, re

def load_src(name):
    p = os.path.join(os.path.dirname(__file__), name + ".py")
    sp = importlib.util.spec_from_file_location(name, p); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    return m

def _plain(s):
    return re.sub(r"<[^>]+>", "", s)

def gateway_table(routes, out_cat, flag_js, home_label, dest_label, skip_origin=()):
    """按 fo（境外城市）汇总：直飞的 cn 城市、承运人、没有直飞的 cn 城市。"""
    flags = dict(re.findall(r"'([^']+)':'([^']+)'", flag_js))
    order, live, gone, cars = [], {}, {}, {}
    for cn, fo, car, fq, wk, dur, cat, note, src in routes:
        if cn in skip_origin: continue
        if fo not in order: order.append(fo)
        if cat == out_cat: gone.setdefault(fo, []); gone[fo].append(cn) if cn not in gone[fo] else None; continue
        live.setdefault(fo, {}); live[fo][cn] = live[fo].get(cn, 0) + wk
        cars.setdefault(fo, [])
        c0 = re.sub(r"[（(][^）)]*[）)]", "", _plain(car))                 # 去括号里的机型/机场
        c0 = re.sub(r"(?<![A-Za-z0-9])[A-Z0-9]{2}\d{1,4}(?:/\d{1,4})?(?![A-Za-z0-9])", "", c0)        # 去航班号
        c0 = re.sub(r"(?<![A-Za-z])[A-Z0-9]{2}(?![A-Za-z])", "", c0)         # 去两字代码 CX/TK/3U
        for c in re.split(r"[·＋+、,，]", c0):
            c = c.strip(" ：:")
            if len(c) >= 2 and c not in cars[fo] and "未核" not in c and c not in ("无", "无直飞", "承运人未核"): cars[fo].append(c)
    order.sort(key=lambda f: -sum(live.get(f, {}).values()))
    rows = []
    for fo in order:
        l = live.get(fo, {})
        cities = " · ".join("%s%s" % (c, "（%d）" % w if w else "") for c, w in sorted(l.items(), key=lambda x: -x[1])) or "<b>无</b>"
        rows.append('<tr><td class="cn">%s %s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            flags.get(fo, ""), fo, cities, " · ".join(cars.get(fo, [])[:8]) or "—", " · ".join(gone.get(fo, [])) or "—"))
    return ('<div class="tblwrap"><table class="wide" style="min-width:760px"><thead><tr><th>%s城市</th><th>直飞%s城市（班/周）</th><th>承运人</th><th>没有直飞的</th></tr></thead><tbody>%s</tbody></table></div>'
            % (dest_label, home_label, "".join(rows)))
