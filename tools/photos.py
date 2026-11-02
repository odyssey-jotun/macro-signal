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
# The guide page uses a couple at a laptop (Unsplash bEQgcVTb1hQ).
for name, src, x in (("laptop", "ztYmIQecyH4", 177), ("phone", "z6w4T4tAOxI", 120), ("couple", "bEQgcVTb1hQ", 560)):
    im = Image.open(f"images/originals/{src}.jpg")
    w, h = im.size
    im = grade(im.crop((x, 0, x + round(h * 4 / 3), h)))
    for tw in (600, 900):
        im.resize((tw, round(tw * 3 / 4)), Image.LANCZOS).save(f"images/{name}-{tw}.webp", quality=74, method=6)
    print("wrote", name)

def crop(im, ratio, fx=0.5, fy=0.5):
    """The largest crop at `ratio`, placed by focus point (0-1 on each axis)."""
    w, h = im.size
    if w / h > ratio:
        nw = round(h * ratio); x = round((w - nw) * fx); return im.crop((x, 0, x + nw, h))
    nh = round(w / ratio); y = round((h - nh) * fy); return im.crop((0, y, w, y + nh))


# Section photos (4:3), all Unsplash. name: (id, focus x, focus y)
SECTIONS = {
    "newspaper": ("Em40ER_I88Y", 0.5, 0.42),   # man reading the business pages over coffee
    "letter": ("mTtTJE6SU78", 0.45, 0.5),      # couple reading a page together at breakfast
    "paperwork": ("WyyP2PsmwKw", 0.5, 0.5),    # couple going over papers at the kitchen table
    "screens": ("vKNRKjSNbTo", 0.5, 0.62),     # trading charts on a tablet and monitors
    "chart-phone": ("K5mPtONmpHM", 0.35, 0.5), # phone held up in front of a stock chart
    "students-phones": ("QCNJ3xGnFR4", 0.5, 0.5),
    "friends-phone": ("Y4zNMW3pQAs", 0.6, 0.5),
}
for name, (src, fx, fy) in SECTIONS.items():
    im = grade(crop(Image.open(f"images/originals/{src}.jpg"), 4 / 3, fx, fy))
    for tw in (600, 900):
        im.resize((tw, round(tw * 3 / 4)), Image.LANCZOS).save(f"images/{name}-{tw}.webp", quality=74, method=6)
    print("wrote", name)

# Tall versions (4:5) for sections whose text runs long beside the photo.
TALL = {
    "newspaper-t": ("Em40ER_I88Y", 0.5, 0.3),
    "paperwork-t": ("WyyP2PsmwKw", 0.5, 0.5),
    "chart-phone-t": ("K5mPtONmpHM", 0.2, 0.5),
}
for name, (src, fx, fy) in TALL.items():
    im = grade(crop(Image.open(f"images/originals/{src}.jpg"), 4 / 5, fx, fy))
    for tw in (600, 900):
        im.resize((tw, round(tw * 5 / 4)), Image.LANCZOS).save(f"images/{name}-{tw}.webp", quality=74, method=6)
    print("wrote", name)

# Research hero: a student studying in a library reading room
# (Unsplash klbApl9mxr0), cropped in close on her desk.
im = grade(Image.open("images/originals/klbApl9mxr0.jpg").crop((1080, 560, 2400, 1550)))
for tw in (600, 900):
    im.resize((tw, round(tw * 3 / 4)), Image.LANCZOS).save(f"images/library-{tw}.webp", quality=74, method=6)
print("wrote library")

# Report card photos (4:3, smaller), one per report.
CARDS = {
    "r-cpi": ("zE95fhGitc0", 0.45, 0.5),        # family shopping at the supermarket
    "r-jobs": ("UQ716eQauSw", 0.62, 0.5),       # "now hiring" sign in a shop window
    "r-unemployment": ("pg2eJwNVpvY", 0.55, 0.5),  # job interview
    "r-rates": ("bqUZEAeWuok", 0.3, 0.5),       # keys to a new home
}
for name, (src, fx, fy) in CARDS.items():
    im = grade(crop(Image.open(f"images/originals/{src}.jpg"), 4 / 3, fx, fy))
    for tw in (480, 720):
        im.resize((tw, round(tw * 3 / 4)), Image.LANCZOS).save(f"images/{name}-{tw}.webp", quality=74, method=6)
    print("wrote", name)

# Closing banner: three friends laughing over dinner (Unsplash xzPq2pQxAFk).
# 8:3 for laptops, cropped so faces sit in the top third, above the text;
# 4:3 for phones.
im = grade(Image.open("images/originals/xzPq2pQxAFk.jpg"))
wide, tall = crop(im, 8 / 3, 0.5, 0.43), crop(im, 4 / 3, 0.62, 0.5)
for tw in (1000, 1600, 2400):
    wide.resize((tw, tw * 3 // 8), Image.LANCZOS).save(f"images/closing-{tw}.webp", quality=72, method=6)
for tw in (600, 900):
    tall.resize((tw, round(tw * 3 / 4)), Image.LANCZOS).save(f"images/closing-m-{tw}.webp", quality=72, method=6)
print("wrote closing")

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
