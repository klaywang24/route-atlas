# -*- coding: utf-8 -*-
"""欧洲 ⇄ 美国（镜像页）：数据借 regions/us_eu.py，只换视角。改航线改 us_eu.py，本文件只管叙事。"""
from _mirror import load_src, gateway_table
E = load_src("us_eu")
MIRROR_OF = "us_eu"
FAMILY = "欧洲出发"
OUT = "欧美航线.html"
ROUTES, GROUPS, OUT_CAT = E.ROUTES, E.GROUPS, E.OUT_CAT

META = dict(E.META,
    title="欧美航线 · 从欧洲哪儿飞美国",
    brand="Westbound", brand_zh="欧美航线",
    h1="欧美航线 · <em>从欧洲哪儿飞美国</em>",
    sub="EUROPE ⇄ UNITED STATES · 十四城 × 十个美国门户 · 2026 夏季 · 镜像自《美欧航线》",
    kicker="给在欧洲的人看的版本：<b>你在哪个城市，能直飞美国哪儿，谁在飞。</b>数据与《美欧航线》同一份，只换视角、流向图默认从欧洲出发。"
           "美国是欧洲人第一大洲际目的地（西欧 2024 年 1,307 万人次），但 <b>2025 起在跌</b>：全年入境 −6～8%，2026 夏提前预订欧→美 −14.2%。"
           "🔴 逐线票价一律未核。",
    origin_label="美国", dest_label="欧洲", default_dir="in",
    mirror="../美国出发/美欧航线.html", mirror_label="美国出发视角《美欧航线》",
)


def sections(rows_of, table, COLS):
    src = E.sections(rows_of, table, COLS)
    by = {s["id"]: s for s in src}
    keep = [sec for sec in src if sec["id"] not in ("s1", "s2")]
    out = [
    dict(id="s1", n="I", nav="你在哪，能飞哪", h="一、你在哪，能飞哪", zh="按欧洲城市看",
         kick="先查你所在的城市。表按欧洲城市分组（按已核总班次排），列它到美国哪些门户有直飞、谁飞。频次未核的行不计入括号里的数。",
         html=gateway_table(ROUTES, OUT_CAT, E.META["flag_js"], "美国", "欧洲") + '''
<div class="callout"><div class="ch">欧洲人去美国，2024–2026 变了什么</div>
<ul class="clean">
  <li><b>体量</b>：2024 年西欧赴美 1,307 万人次；英国 404 万（2019 年的 84%）、德国 200 万（97%）、意大利已超 2019。</li>
  <li><b>2025 转跌</b>：美国全年入境 −6～8%，西欧 3 月 −17%、11 月 −5.5%，德国下滑最明显；2026 夏提前预订欧→美 −14.2%，法兰克福 −36%。</li>
  <li><b>航权</b>：美欧开放天空，没有配额；三大合资体（达美/法荷航/维珍 · 美联航/汉莎集团 · 美航/英航/伊比利亚）拿走八成五以上运力，廉价长途在退潮。</li>
  <li><b>都柏林有美国预检</b>：在都柏林过美国海关，落地美国走国内到达。</li>
</ul></div>'''),
    dict(id="s2", n="II", nav="流向图", h="二、流向图", zh="默认欧洲 → 美国",
         kick="<b>红线＝美国航司，绿线＝对方航司，灰虚线＝无直飞。</b>默认只显示欧洲出发方向，切「双向」看全貌。",
         html='<div id="flow"></div>'),
    ]
    return out + keep
