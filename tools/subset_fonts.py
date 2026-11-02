#!/usr/bin/env python3
"""Re-subset the self-hosted fonts to the characters the built pages use.

Needs fontTools and brotli:  pip install fonttools brotli
Run from the repo root after `python3 build.py`:  python3 tools/subset_fonts.py
Originals (Fontsource latin files) are in tools/font-src/.
"""
import glob, html, os, re
from fontTools import subset
from fontTools.ttLib import TTFont

text = ""
for f in glob.glob("*.html"):
    t = open(f).read()
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", t, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    text += html.unescape(t)
chars = set(text) | set(chr(c) for c in range(32, 127)) | set("‘’“”·…→−")

JOBS = [("tools/font-src/ibm-plex-sans-latin-400-normal.woff2", "fonts/plex-sans-400.woff2"),
        ("tools/font-src/ibm-plex-sans-latin-700-normal.woff2", "fonts/plex-sans-700.woff2"),
        ("tools/font-src/ibm-plex-mono-latin-500-normal.woff2", "fonts/plex-mono-500.woff2")]
for src, out in JOBS:
    font = TTFont(src)
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga", "calt", "lnum", "pnum", "tnum"]
    opts.notdef_outline = True
    sub = subset.Subsetter(opts)
    sub.populate(unicodes=[ord(c) for c in chars if c.strip() or c == " "])
    sub.subset(font)
    font.flavor = "woff2"
    font.save(out)
    print("wrote", out, os.path.getsize(out), "bytes")
