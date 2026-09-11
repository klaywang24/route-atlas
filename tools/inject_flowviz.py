#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 flow-viz skill 的嵌入式运行时注入宿主页（唯一实现在 ~/.claude/skills/flow-viz/flowviz.py）。
用法：
  python3 tools/inject_flowviz.py inject <html...>   # 注入或更新（放在 </head> 前；无 </head> 的模板放在第一个 <style 前）
  python3 tools/inject_flowviz.py --check           # 全部页面里的运行时块必须与 skill 当前版本逐字节一致
用法：先 build_region_page.py 生成，再本工具 inject，再 build_theme.py。"""
import io, os, re, sys
sys.path.insert(0, os.path.expanduser("~/.claude/skills/flow-viz"))
import flowviz
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGETS = sorted(os.path.join(d, f) for d in ("中国出发", "美国出发", "欧洲出发")
                 if os.path.isdir(os.path.join(HERE, d))
                 for f in os.listdir(os.path.join(HERE, d)) if f.endswith(".html")) + [os.path.join(HERE, "index.html")]  # 三家族目录下全部页面 ＋ 站首页
PAT = re.compile(r"<!-- flowviz:runtime v[^>]*-->.*?<!-- /flowviz:runtime -->", re.S)

def inject(path):
    s = io.open(path, encoding="utf-8").read(); blk = flowviz.runtime_block()
    if PAT.search(s): s2 = PAT.sub(lambda m: blk, s, count=1)
    else:
        if "</head>" in s: s2 = s.replace("</head>", blk + "\n</head>", 1)
        else: k = s.index("<style"); s2 = s[:k] + blk + "\n" + s[k:]
    io.open(path, "w", encoding="utf-8").write(s2); print("✅ 注入", os.path.relpath(path, HERE), "v" + flowviz.EMBED_VERSION)

def check():
    blk = flowviz.runtime_block(); bad = 0; n = 0
    for t in TARGETS:
        p = os.path.join(HERE, t)
        if not os.path.exists(p): continue
        s = io.open(p, encoding="utf-8").read(); m = PAT.search(s)
        if not m: continue
        n += 1
        if m.group(0) != blk: bad += 1; print("🔴 flowviz 运行时漂移：", t, "（跑 tools/inject_flowviz.py inject 该文件）")
    if bad: sys.exit(1)
    print("✅ flowviz 运行时 %d 处与 skill v%s 一致" % (n, flowviz.EMBED_VERSION))

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--check": check()
    elif len(sys.argv) > 2 and sys.argv[1] == "inject":
        for f in sys.argv[2:]: inject(os.path.join(HERE, f) if not os.path.isabs(f) else f)
    else: print(__doc__)
