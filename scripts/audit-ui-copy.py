#!/usr/bin/env python3
"""Blocking quality gate: no terminal periods in visible UI copy.

Scans text nodes, alt/title/aria-label/placeholder attributes, the document
title, meta description and og/twitter tags, plus strings assigned from JS.
Also reports em/en dashes so they can be triaged by hand (a range like
0-100 km/h is fine, prose dashes are not).

Usage: python3 scripts/audit-ui-copy.py index.html en/index.html
Exit code 1 if any terminal period is found.
"""
import re, pathlib, sys, html as H
FILES=[pathlib.Path(p) for p in sys.argv[1:]]
def strip_tags_regions(s):
    # remove script/style bodies but keep track separately
    return re.sub(r"<(script|style)\b.*?</\1>", "", s, flags=re.S|re.I)
def text_nodes(doc):
    out=[]
    for m in re.finditer(r">([^<>]+)<", doc):
        t=H.unescape(m.group(1)).strip()
        if t: out.append(("text", t))
    return out
def attrs(doc):
    out=[]
    for m in re.finditer(r'(alt|title|aria-label|placeholder|content)\s*=\s*"([^"]*)"', doc, re.I):
        k,v=m.group(1).lower(), H.unescape(m.group(2)).strip()
        if not v: continue
        if k=="content" and not re.search(r'(description|og:|twitter:)', doc[max(0,m.start()-160):m.start()], re.I): continue
        out.append((k, v))
    return out
def js_strings(s):
    out=[]
    for m in re.finditer(r"(?:textContent|innerHTML|innerText|setAttribute\([^,]+,)\s*=?\s*([`'\"])(.*?)\1", s, re.S):
        v=m.group(2).strip()
        if v: out.append(("js", v))
    return out
bad=0
for f in FILES:
    raw=f.read_text(); doc=strip_tags_regions(raw)
    print(f"== {f}")
    for kind,t in text_nodes(doc)+attrs(doc)+js_strings(raw):
        if t.endswith(".") and not re.search(r"\b[A-Za-zА-Яа-я]\.$", t) is None or t.endswith("."):
            bad+=1; print(f"   PERIOD [{kind}] {t[:120]}")
        elif "—" in t or "–" in t:
            print(f"   dash   [{kind}] {t[:120]}")
print("periods:",bad); sys.exit(1 if bad else 0)
