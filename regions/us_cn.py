# -*- coding: utf-8 -*-
"""美国 ⇄ 中国大陆（镜像页）：数据借 regions/usa.py，只换视角。改航线改 usa.py，本文件只管叙事。"""
MIRROR_OF = "usa"
FAMILY = "美国出发"
OUT = "美中航线.html"

CN = "中国航司"; FO = "美国航司"; OUT_CAT = "需中转"
WEST={"洛杉矶","旧金山","西雅图"}; EAST={"纽约","华盛顿","波士顿"}; MID={"芝加哥","底特律","达拉斯"}

META = dict(
    title="美中航线 · 从美国哪儿飞回去",
    brand="Homebound", brand_zh="美中航线",
    h1="美中航线 · <em>从美国哪儿飞回去</em>",
    sub="UNITED STATES ⇄ CHINA · 2026-09-10 · 镜像自《中美航线》",
    kicker="给在美国的人看的版本：<b>你在哪个城市，能直飞回哪儿。</b>数据与《中美航线》同一份，只换视角、流向图默认从美国出发。"
           "一句话：<b>西岸三城最密，东岸只有中方航司在飞，中部只有达拉斯和底特律各一条每日，芝加哥没有直飞。</b>"
           "🔴 中美双边各 50 班/周硬顶已用满，短期不会有新对。",
    footer="中国出发 · 美国出发 · 欧洲出发 三家族同一设计系统，与 <a href=\"https://chronicle.klay-wang.com\">Market Chronicle</a> 同源 · 班次按每方向每周 · 逐线票价一律未核 · 换季重核",
    cat_js="{'中国航司':'var(--accent)','美国航司':'var(--teal,#00A86B)','需中转':'var(--muted-soft,#9B8E7C)'}",
    flag_js="{'纽约':'🇺🇸','华盛顿':'🇺🇸','波士顿':'🇺🇸','洛杉矶':'🇺🇸','旧金山':'🇺🇸','西雅图':'🇺🇸','芝加哥':'🇺🇸','底特律':'🇺🇸','达拉斯':'🇺🇸'}",
    origin_label="中国", dest_label="美国", default_dir="in",
    mirror="../中国出发/中美航线.html", mirror_label="中国出发视角《中美航线》",
)


def sections(rows_of, table, COLS):
    ML = [r for r in ROUTES if r[0] != "香港"]   # 大陆行；香港只在第六节出现一次，避免流向图重复计数
    return [
    dict(id="s1", n="I", nav="你在哪，能飞回哪", h="一、你在哪，能飞回哪", zh="按美国城市看",
         kick="先查你所在的城市。表按美国门户分组，每组列它到大陆哪些城市有直飞、谁飞、一周几班。",
         html='''
<div class="tblwrap"><table class="wide" style="min-width:720px">
<thead><tr><th>美国城市</th><th>直飞大陆</th><th>承运人</th><th>没有的</th></tr></thead><tbody>
<tr><td class="cn">🇺🇸 洛杉矶</td><td>上海（三家）· 北京（两家）· 广州 · 深圳 · 厦门 · 成都</td><td>美联航 · 达美 · 东航 · 国航 · 南航 · 厦航 · 川航</td><td>—</td></tr>
<tr><td class="cn">🇺🇸 旧金山</td><td>上海（两家）· 北京（两家）· 广州 · 武汉</td><td>美联航 · 东航 · 国航 · 南航</td><td>—</td></tr>
<tr><td class="cn">🇺🇸 西雅图</td><td>上海 · 北京 · 重庆</td><td>达美 · 海航</td><td>—</td></tr>
<tr><td class="cn">🇺🇸 纽约</td><td>北京 · 上海 · 广州 · 福州</td><td>国航 · 东航 · 南航 · 厦航（<b>全是中方</b>）</td><td>美联航纽瓦克线 2026 名单无</td></tr>
<tr><td class="cn">🇺🇸 华盛顿</td><td>北京</td><td>国航</td><td>美联航申请继续停飞</td></tr>
<tr><td class="cn">🇺🇸 波士顿</td><td>北京</td><td>海航</td><td>—</td></tr>
<tr><td class="cn">🇺🇸 达拉斯</td><td>上海</td><td>美航（每日，<b>美航唯一大陆线</b>）</td><td>—</td></tr>
<tr><td class="cn">🇺🇸 底特律</td><td>上海</td><td>达美（每日）</td><td>—</td></tr>
<tr><td class="cn">🇺🇸 芝加哥</td><td><b>无</b></td><td>—</td><td>美联航两条芝加哥线都在申请继续停飞；经旧金山/洛杉矶/西雅图/底特律</td></tr>
</tbody></table></div>
<div class="callout"><div class="ch">🇭🇰 香港是第二条路，不占配额</div>
<p>国泰从纽约、旧金山、洛杉矶、西雅图、芝加哥、波士顿、达拉斯七个点直飞香港，美联航飞纽瓦克与旧金山，美航飞达拉斯。<b>芝加哥和波士顿没有大陆直飞，但有每日香港</b>，回华南走这条比转西岸顺。</p></div>'''),

    dict(id="s2", n="II", nav="流向图", h="二、流向图", zh="默认美国 → 中国",
         kick="<b>绿线＝美国航司，红线＝中国航司，灰虚线＝需中转。</b>默认只显示美国出发方向，切「双向」看全貌。",
         html='<div id="flow"></div>'),

    dict(id="s3", n="III", nav="西岸", h="三、西岸", zh="洛杉矶 · 旧金山 · 西雅图",
         kick="美方三家的中国线几乎全在这里：美联航旧金山与洛杉矶各两条，达美西雅图与洛杉矶。",
         html=table(rows_of(ML, WEST, skip=OUT_CAT), COLS) + "<h3>需中转</h3>" + table(rows_of(ML, WEST, cat=OUT_CAT), COLS)),

    dict(id="s4", n="IV", nav="东岸", h="四、东岸", zh="纽约 · 华盛顿 · 波士顿",
         kick="东岸没有一条美方航司的大陆线，全靠国航东航南航厦航海航。",
         html=table(rows_of(ML, EAST, skip=OUT_CAT), COLS) + "<h3>需中转</h3>" + table(rows_of(ML, EAST, cat=OUT_CAT), COLS)),

    dict(id="s5", n="V", nav="中部", h="五、中部", zh="达拉斯 · 底特律 · 芝加哥",
         kick="达拉斯美航每日、底特律达美每日，都是上海。芝加哥零直飞。",
         html=table(rows_of(ML, MID, skip=OUT_CAT), COLS) + "<h3>需中转</h3>" + table(rows_of(ML, MID, cat=OUT_CAT), COLS)),

    dict(id="s6", n="VI", nav="香港 · 配额外", h="六、美国 ⇄ 香港", zh="不占中美配额",
         kick="",
         html=table(rows_of([r for r in ROUTES if r[0]=="香港"]), COLS)),

    dict(id="s7", n="VII", nav="配额与口径", h="七、配额与口径", zh="为什么短期不会有新对",
         kick="",
         html='''
<div class="callout"><div class="ch">中美各 50 班/周，2026-10-06 起 100/100</div>
<ul class="clean">
  <li>美方：美联航 24 ＋ 达美 19 ＋ 美航 7 ＝ 50。达美 10/6 洛杉矶–上海加两班用掉最后两个位子。</li>
  <li>中方：国航 14 ＋ 东航 12 ＋ 南航 10 ＋ 海航 6 ＋ 厦航 5 ＋ 川航 3 ＝ 50。</li>
  <li>美联航 2026-02-18 仍正式申请继续停飞 42 班（芝加哥、纽瓦克、华盛顿各线），<b>不缺额度缺需求</b>。所以芝加哥和纽瓦克短期不会回来。</li>
  <li>完整口径、来源、未核项见镜像源《中美航线》第八节，本页不重复。</li>
</ul></div>'''),
    ]
