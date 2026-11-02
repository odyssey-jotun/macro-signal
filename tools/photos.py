#!/usr/bin/env python3
"""Crop, color-grade and export the site photos from images/originals/ (gitignored).
Run from the repo root: python3 tools/photos.py
"""
from PIL import Image, ImageOps, ImageEnhance, ImageDraw, ImageFont


def grade(im):
    im = ImageOps.autocontrast(im.convert("RGB"), cutoff=0.5)
    return ImageEnhance.Color(im).enhance(1.04)


# Julian (4:5), from Caroline's "Photo of Julian" email, 2026-10-29.
im = grade(ImageOps.exif_transpose(Image.open("images/originals/julian.jpg")).crop((430, 600, 3830, 4850)))
for w in (480, 680, 800):
    im.resize((w, round(w * 5 / 4)), Image.LANCZOS).save(f"images/julian-{w}.webp", quality=72, method=6)
print("wrote julian")

# Home banner: a smiling man reading his phone over coffee in his kitchen
# (Unsplash w6CqGUuD_q8). 2:1 for laptops, 4:3 for phones.
im = grade(Image.open("images/originals/w6CqGUuD_q8.jpg"))
w, h = im.size
wide = im.crop((0, round((h - w / 2) * 0.3), w, round((h - w / 2) * 0.3 + w / 2)))
for tw in (1000, 1600, 2400):
    wide.resize((tw, tw // 2), Image.LANCZOS).save(f"images/banner-{tw}.webp", quality=72, method=6)
cw = round(h * 4 / 3)
cx = round(w * 0.58 - cw / 2)
tall = im.crop((cx, 0, cx + cw, h))
for tw in (600, 900):
    tall.resize((tw, round(tw * 3 / 4)), Image.LANCZOS).save(f"images/banner-m-{tw}.webp", quality=72, method=6)
print("wrote banner")

# Stock, 4:3: laptop with a stock chart (Unsplash ztYmIQecyH4) and a woman
# reading her phone at a cafe (Unsplash z6w4T4tAOxI).
for name, src, x in (("laptop", "ztYmIQecyH4", 177), ("phone", "z6w4T4tAOxI", 120)):
    im = Image.open(f"images/originals/{src}.jpg")
    w, h = im.size
    im = grade(im.crop((x, 0, x + round(h * 4 / 3), h)))
    for tw in (600, 900):
        im.resize((tw, round(tw * 3 / 4)), Image.LANCZOS).save(f"images/{name}-{tw}.webp", quality=74, method=6)
    print("wrote", name)

# Link preview (og.jpg): the tagline on terminal navy. Never Julian's face.
card = Image.new("RGB", (1200, 630), (13, 27, 46))
d = ImageDraw.Draw(card)
font = ImageFont.truetype("tools/font-src/IBMPlexSans-Bold.ttf", 92)
small = ImageFont.truetype("tools/font-src/IBMPlexSans-Bold.ttf", 34)
d.line([(96, 150), (190, 110), (260, 135), (380, 70)], fill=(111, 211, 166), width=8, joint="curve")
d.text((96, 200), "The economy,", font=font, fill=(255, 255, 255))
d.text((96, 310), "read for you.", font=font, fill=(111, 211, 166))
d.text((96, 460), "An AI agent that reads the economic news", font=small, fill=(174, 187, 204))
card.save("images/og.jpg", quality=88)
print("wrote og.jpg")
