# -*- coding: utf-8 -*-
"""欧洲 ⇄ 中国大陆（镜像页）：数据借 regions/europe.py，只换视角。改航线改 europe.py，本文件只管叙事。"""
from _mirror import load_src, gateway_table
E = load_src("europe")
MIRROR_OF = "europe"
FAMILY = "欧洲出发"
OUT = "欧中航线.html"
ROUTES, GROUPS, OUT_CAT = E.ROUTES, E.GROUPS, E.OUT_CAT

META = dict(E.META,
    title="欧中航线 · 从欧洲哪儿飞中国",
    brand="Eastbound", brand_zh="欧中航线",
    h1="欧中航线 · <em>从欧洲哪儿飞中国</em>",
    sub="EUROPE ⇄ CHINA · 十三国 ＋ 香港 · 2026-09-11 · 镜像自《中欧航线》",
    kicker="给在欧洲的人看的版本：<b>你在哪个城市，能直飞中国哪儿，谁在飞。</b>数据与《中欧航线》同一份，只换视角、流向图默认从欧洲出发。"
           "一句话：<b>欧洲航司退了一大半，现在飞中国的八成是中国航司；法德意荷西免签 30 天到 2026 底，英国不免签。</b>"
           "🔴 逐线票价一律未核。",
    origin_label="中国", dest_label="欧洲", default_dir="in",
    mirror="../中国出发/中欧航线.html", mirror_label="中国出发视角《中欧航线》",
)


def sections(rows_of, table, COLS):
    src = E.sections(rows_of, table, COLS)
    by = {s["id"]: s for s in src}
    keep = [sec for sec in src if sec["id"] not in ("s1", "s2")]
    out = [
    dict(id="s1", n="I", nav="你在哪，能飞哪", h="一、你在哪，能飞哪", zh="按欧洲城市看",
         kick="先查你所在的城市。表按欧洲城市分组（按总班次排），列它到大陆哪些城市有直飞、谁飞。香港单列在第十二节。",
         html=gateway_table(E.ML, OUT_CAT, E.META["flag_js"], "中国", "欧洲") + '''
<div class="callout"><div class="ch">欧洲人去中国，2024–2026 变了什么</div>
<ul class="clean">
  <li><b>免签</b>：2023-12-01 起法德意荷西单方面免签，2024-11-30 起扩到 38 国、30 天，已延至 2026-12-31。2025 年外国人免签入境 3,008 万（占 73%），<b>欧洲免签访华 200 万+</b>，北京欧洲客 +47.9%。<b>英国不在免签名单</b>，英国居民 2024 年去大陆 59.8 万人次，七成二是探亲。</li>
  <li><b>航司换了人</b>：英航北京、维珍上海、北欧航空上海、LOT 北京、汉莎北京 2024 年全停；中国航司占中欧航班八成二（疫前五成六）。<b>运力没减，只是换了承运人。</b></li>
  <li><b>时长</b>：欧洲航司不能飞俄领空，伦敦–上海 11h→13h、哥本哈根–上海 10h30→12h30；中国航司走俄领空，同一对城市短 1–2 小时。选中国航司通常更快也更便宜。</li>
</ul></div>'''),
    dict(id="s2", n="II", nav="流向图", h="二、流向图", zh="默认欧洲 → 中国",
         kick="<b>红线＝中国航司，绿线＝欧洲航司，灰虚线＝已退出。</b>默认只显示欧洲出发方向，切「双向」看全貌。",
         html='<div id="flow"></div>'),
    ]
    return out + keep
