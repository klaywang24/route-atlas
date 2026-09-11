#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把某页的流向图录成动图（README 用）。GitHub README 跑不了 JS，只能放 GIF；粒子在动就是「动态」了。
用法：
  python3 -m venv .pwenv && .pwenv/bin/pip install playwright pillow      # 一次性；用系统 Chrome，不下载浏览器
  .pwenv/bin/python tools/record_flow_gif.py index.html docs/img/flow_world.gif --size 1180x530 [--dir out] [--frames 36 --dt 90]
  .pwenv/bin/python tools/record_flow_gif.py 中国出发/中美航线.html docs/img/flow_cn_us.gif --size 1180x590 --dir out   # 单向视角，双向太密
做法：复制页面 → 追加一段只显示 #flow 的 CSS（放 </body> 前才压得住主题样式）→ 可选把默认方向改成单向 → Playwright 开系统 Chrome 连拍 → Pillow 合成 GIF。
"""
import io, os, sys, tempfile
from playwright.sync_api import sync_playwright
from PIL import Image

CSS = '''<style id="shot">
html{color-scheme:light}
#tocBtn,#darkBtn,.starfield,.toc-sidebar,.toc-backdrop,.fam,footer,h1,.sub,.kicker{display:none!important}
.wrap>*{display:none!important}
.wrap>#flow{display:block!important;margin:0!important}
.wrap{max-width:1100px!important;padding:16px 0 0!important;margin:0 auto!important}
body{padding:0!important}
</style>'''

def main(argv):
    src, dst = argv[1], argv[2]
    size = argv[argv.index("--size") + 1] if "--size" in argv else "1180x700"
    direction = argv[argv.index("--dir") + 1] if "--dir" in argv else None
    n = int(argv[argv.index("--frames") + 1]) if "--frames" in argv else 36
    dt = int(argv[argv.index("--dt") + 1]) if "--dt" in argv else 90
    w, h = map(int, size.split("x"))
    s = io.open(src, encoding="utf-8").read()
    if direction: s = s.replace("var dir='both', grp='';", "var dir='%s', grp='';" % direction, 1)
    s = s.replace("</body>", CSS + "\n</body>", 1) if "</body>" in s else s + CSS
    tmp = os.path.join(os.path.dirname(os.path.abspath(src)), "_shot_tmp.html")   # 与源页同目录，相对资源才找得到
    io.open(tmp, "w", encoding="utf-8").write(s)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(channel="chrome", headless=True)
            pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
            pg.goto("file://" + os.path.abspath(tmp)); pg.wait_for_timeout(2500)
            frames = []
            for _ in range(n):
                frames.append(Image.open(io.BytesIO(pg.screenshot())).convert("RGB")
                              .quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE))
                pg.wait_for_timeout(dt)
            b.close()
    finally:
        os.remove(tmp)
    frames[0].save(dst, save_all=True, append_images=frames[1:], duration=dt, loop=0, optimize=True)
    print("✅", dst, os.path.getsize(dst) // 1024, "KB")

if __name__ == "__main__":
    main(sys.argv)
