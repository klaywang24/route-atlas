#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 theme.css 注入三家族目录下全部 HTML，替换各自原有的 :root 调色块。

    python3 build_theme.py            注入（幂等）
    python3 build_theme.py --check    只读；有文件与 theme.css 不一致就退 1

规矩：一处判据只能有一个实现。调色板的唯一实现是 theme.css，
HTML 里 THEME:START/END 之间的内容是生成物，手改会被下次生成覆盖。

安全性：只删整块都是 --x:y 声明的规则块，删之前逐块验过；
删完断言每个文件里引用到的 var(--x) 都仍有定义，缺一个就报错不写盘。
"""
import io, os, re, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 仓根（本文件在 tools/）
START, END = "<!-- THEME:START -->", "<!-- THEME:END -->"
FILES = sorted([os.path.join(d, f) for d in ("中国出发", "美国出发", "欧洲出发")
                if os.path.isdir(os.path.join(HERE, d))
                for f in os.listdir(os.path.join(HERE, d)) if f.endswith(".html")]
               + (["index.html"] if os.path.exists(os.path.join(HERE, "index.html")) else []))  # 三家族目录下全部页面 + 站首页

# 只含自定义属性的规则块：:root / :root[...] / [data-theme=...] / 包着 :root 的深色媒体查询
PAL = re.compile(
    r'(?:@media[^{]*prefers-color-scheme[^{]*\{\s*)?'
    r':root(?:\[[^\]]*\])?(?::not\([^)]*\))?\s*\{[^{}]*\}\s*\}?'
    r'|\[data-theme="[^"]*"\]\s*\{[^{}]*\}')

def is_pure(block):
    body = re.search(r'\{([^{}]*)\}', block)
    if not body: return False
    decls = re.findall(r'[\w-]+\s*:', body.group(1))
    custom = re.findall(r'--[\w-]+\s*:', body.group(1))
    return bool(custom) and len(decls) == len(custom)

def strip_palette(s):
    """删掉纯变量声明的调色块，返回 (新文本, 删除数)。非纯的一律不动。"""
    out, n = [], 0
    last = 0
    for m in PAL.finditer(s):
        if not is_pure(m.group(0)): continue
        out.append(s[last:m.start()]); last = m.end(); n += 1
    out.append(s[last:])
    return "".join(out), n

def defined(theme):
    return set(re.findall(r'--([\w-]+)\s*:', theme))

def referenced(s):
    # 只看 <style> 里的引用；行内 style 属性也算
    return set(re.findall(r'var\(\s*--([\w-]+)', s))

def build(check=False):
    theme = io.open(os.path.join(HERE, "theme.css"), encoding="utf-8").read().strip()
    blk = "%s<style id=\"fm-theme\">\n%s\n</style>%s" % (START, theme, END)
    have = defined(theme)
    bad, changed = [], []

    for f in FILES:
        p = os.path.join(HERE, f)
        s0 = io.open(p, encoding="utf-8").read()
        if START in s0:
            i, j = s0.index(START), s0.index(END) + len(END)
            s = s0[:i] + blk + s0[j:]
        else:
            s, n = strip_palette(s0)
            k = s.index("<style")
            s = s[:k] + blk + "\n" + s[k:]
            if not n:
                bad.append((f, "没找到可替换的调色块")); continue

        # 允许本页自己定义的派生色（如房券页分布条的 band/band2）：
        # 判据是共享定义 ∪ 本页定义都覆盖不到才算缺失
        local = defined(s[s.index(END) + len(END):] + s[:s.index(START)])
        miss = sorted(r for r in referenced(s) if r not in have and r not in local)
        if miss:
            bad.append((f, "注入后仍有未定义的变量: %s" % ", ".join(miss[:8]))); continue
        if s != s0: changed.append((f, p, s))

    if bad:
        for f, why in bad: print("❌ %-20s %s" % (f, why))
        return 1
    if check:
        if changed:
            for f, _, _ in changed: print("❌ %-20s 调色板与 theme.css 不一致" % f)
            print("\n⇒ 跑 python3 build_theme.py 重新注入；要改颜色请改 theme.css，别改 HTML。")
            return 1
        print(f"✅ {len(FILES)} 份 HTML 的调色板与 theme.css 一致")
        return 0
    for f, p, s in changed:
        io.open(p, "w", encoding="utf-8").write(s)
        print("✅ %-20s 已注入" % f)
    if not changed: print(f"（{len(FILES)} 份均已是最新，无改动）")
    return 0

if __name__ == "__main__":
    sys.exit(build("--check" in sys.argv))
