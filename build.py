#!/usr/bin/env python3
"""Builds every page of the site, plus sitemap.xml, robots.txt and favicon.svg.

Run: python3 build.py
The site name lives in SITE_NAME below. Change it there, rebuild, and every
page title, wordmark, footer and JSON-LD block follows. Copy and facts live
in this file too, so a correction is made once.
"""
import glob
import json
import os
import re

# ---------------------------------------------------------------- settings
SITE_NAME = "Macro Signal"  # working name until Julian picks one
AUTHOR = "Julian Sassoon"
SITE = "https://odyssey-jotun.github.io/macro-signal/"
TODAY = "2026-11-01"
# Preview only: kept out of search until the name is final.
ROBOTS = "noindex,nofollow"

# Sources, cited in plain text. No links on purpose.
SOURCES = {
    "choice": "Sethi-Iyengar, Sheena, Gur Huberman and Wei Jiang. <em>How Much Choice Is Too Much? Contributions to 401(k) Retirement Plans.</em> In <em>Pension Design and Structure</em>, edited by Olivia S. Mitchell and Stephen P. Utkus. Oxford University Press, 2004.",
    "literacy": "Lusardi, Annamaria, and Olivia S. Mitchell. <em>The Economic Importance of Financial Literacy: Theory and Evidence.</em> Journal of Economic Literature 52, no. 1 (2014): 5-44.",
    "overload": "Agnew, Julie R., and Lisa R. Szykman. <em>Asset Allocation and Information Overload.</em> Journal of Behavioral Finance 6, no. 2 (2005): 57-70.",
    "taiwan": "Barber, Brad M., Yi-Tsung Lee, Yu-Jane Liu and Terrance Odean. <em>Just How Much Do Individual Investors Lose by Trading?</em> Review of Financial Studies 22, no. 2 (2009): 609-632.",
    "hazardous": "Barber, Brad M., and Terrance Odean. <em>Trading Is Hazardous to Your Wealth: The Common Stock Investment Performance of Individual Investors.</em> Journal of Finance 55, no. 2 (2000): 773-806.",
    "glitters": "Barber, Brad M., and Terrance Odean. <em>All That Glitters: The Effect of Attention and News on the Buying Behavior of Individual and Institutional Investors.</em> Review of Financial Studies 21, no. 2 (2008): 785-818.",
    "robinhood": "Barber, Brad M., Xing Huang, Terrance Odean and Christopher Schwarz. <em>Attention-Induced Trading and Returns: Evidence from Robinhood Users.</em> Journal of Finance 77, no. 6 (2022): 3141-3190.",
}

# ---------------------------------------------------------------- the data
# The free guide: one card per report. Facts from the publishing agencies.
REPORTS = [
    {"id": "cpi", "photo": "r-cpi", "alt": "A mother, father and young son shopping for groceries together", "short": "How fast prices are rising, from groceries to rent.", "icon": "shopping-cart", "name": "Consumer Price Index", "series": "CUSR0000SA0",
     "measures": "How much the prices people pay for everyday goods and services changed, from groceries and gas to rent.",
     "who": "U.S. Bureau of Labor Statistics", "when": "Monthly, around the middle of the month, at 8:30 a.m. Eastern",
     "why": "It is the best-known measure of inflation. When prices rise quickly, the Federal Reserve can keep interest rates higher for longer."},
    {"id": "jobs", "photo": "r-jobs", "alt": "A red and white now hiring sign in a shop window", "short": "How many jobs employers added or cut last month.", "icon": "briefcase", "name": "Payroll jobs", "series": "CES0000000001",
     "measures": "How many jobs employers added or cut last month, outside of farm work.",
     "who": "U.S. Bureau of Labor Statistics, in the monthly jobs report", "when": "Usually the first Friday of the month, at 8:30 a.m. Eastern",
     "why": "It is one of the clearest signs of whether the economy is growing or slowing, and it often moves markets the morning it comes out."},
    {"id": "unemployment", "photo": "r-unemployment", "alt": "A woman interviewing a job candidate across an office desk", "short": "The share of people looking for work.", "icon": "search", "name": "Unemployment rate", "series": "LNS14000000",
     "measures": "The share of people who want a job, are looking for one and don't have one.",
     "who": "U.S. Bureau of Labor Statistics, in the same jobs report", "when": "Usually the first Friday of the month, at 8:30 a.m. Eastern",
     "why": "The Federal Reserve's job is to keep prices stable and employment high, so it watches this number closely."},
    {"id": "rates", "photo": "r-rates", "alt": "A hand holding the keys to a new home", "short": "The rate that sets the cost of borrowing.", "icon": "landmark", "name": "Federal funds rate", "series": "RIFSPFF_N.M",
     "measures": "The interest rate banks charge each other to borrow overnight. The Federal Reserve sets a target range for it.",
     "who": "Federal Reserve", "when": "Decided at eight scheduled meetings a year, announced at 2:00 p.m. Eastern",
     "why": "It ripples out to the rates on mortgages, car loans, credit cards and savings accounts."},
]

# ---------------------------------------------------------------- helpers
CSS = None


def css():
    """styles.css, minified and inlined so no stylesheet blocks first paint."""
    global CSS
    if CSS is None:
        t = open("styles.css").read()
        t = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
        t = re.sub(r"\s+", " ", t)
        t = re.sub(r"\s*([{};:,>])\s*", r"\1", t).replace(";}", "}")
        CSS = t.strip()
    return CSS


PORTRAIT_SIZES = "(max-width: 860px) min(calc(100vw - 40px), 340px), 440px"


def portrait(name, alt, eager=False):
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<figure class="portrait"><img src="images/{name}-800.webp" srcset="images/{name}-480.webp 480w, images/{name}-680.webp 680w, images/{name}-800.webp 800w" '
            f'sizes="{PORTRAIT_SIZES}" width="800" height="1000" alt="{alt}" {load} decoding="async"></figure>')


def photo(name, alt, eager=False, tall=False):
    """A 4:3 section photo, or a 4:5 one (tall=True) beside long text."""
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    if tall:
        name, cls, h = name + "-t", "photo tall", 1125
    else:
        cls, h = "photo", 675
    return (f'<figure class="{cls}"><img src="images/{name}-900.webp" srcset="images/{name}-600.webp 600w, images/{name}-900.webp 900w" '
            f'sizes="(max-width: 860px) calc(100vw - 40px), 520px" width="900" height="{h}" alt="{alt}" {load} decoding="async"></figure>')


def preload(name):
    return (f'<link rel="preload" as="image" type="image/webp" href="images/{name}-800.webp" '
            f'imagesrcset="images/{name}-480.webp 480w, images/{name}-680.webp 680w, images/{name}-800.webp 800w" '
            f'imagesizes="{PORTRAIT_SIZES}" fetchpriority="high">\n')


BANNER_PRELOAD = ('<link rel="preload" as="image" type="image/webp" media="(min-width: 861px)" href="images/hero-1500.webp" '
                  'imagesrcset="images/hero-1000.webp 1000w, images/hero-1500.webp 1500w, images/hero-2000.webp 2000w" imagesizes="70vw" fetchpriority="high">\n'
                  '<link rel="preload" as="image" type="image/webp" media="(max-width: 860px)" href="images/hero-m-900.webp" '
                  'imagesrcset="images/hero-m-600.webp 600w, images/hero-m-900.webp 900w" imagesizes="100vw" fetchpriority="high">\n')


PERSON = {
    "@type": "Person", "@id": SITE + "#julian", "name": AUTHOR,
    "description": f"High school junior in Georgia building {SITE_NAME}, an AI agent that reads U.S. economic data and paper trades on it.",
}


def head(title, desc, path="", schema=None, pre=""):
    url = SITE + path
    graph = [{"@type": "WebSite", "@id": SITE + "#site", "url": SITE, "name": SITE_NAME,
              "description": "Deep economics made instant. An AI that reads the four economic reports that move the market and explains each one in plain English.",
              "author": {"@id": SITE + "#julian"}, "inLanguage": "en-US"}, PERSON]
    graph += schema or []
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, separators=(",", ":"))
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="{ROBOTS}">
<link rel="canonical" href="{url}">
<meta name="author" content="{AUTHOR}">
<meta name="theme-color" content="#0D1B2E">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}images/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Deep economics made instant. An AI that explains the economic reports in plain English.">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
{pre}<link rel="preload" href="fonts/plex-sans-700.woff2" as="font" type="font/woff2" crossorigin>
<style>{css()}</style>
<script type="application/ld+json">{ld}</script>
</head>
<body>

<a class="skip" href="#main">Skip to content</a>
"""


def page_schema(kind, path, title, desc, extra=None):
    d = {"@type": kind, "@id": SITE + path + "#page", "url": SITE + path, "name": title,
         "description": desc, "isPartOf": {"@id": SITE + "#site"}, "author": {"@id": SITE + "#julian"},
         "inLanguage": "en-US", "datePublished": TODAY, "dateModified": TODAY, "image": SITE + "images/og.jpg"}
    d.update(extra or {})
    return d


PAGES = [("index.html", "Home"), ("guide.html", "Report Guide"), ("research.html", "Research"), ("updates.html", "Build Updates")]


def wordmark():
    words = SITE_NAME.split()
    if len(words) > 1:
        return f'<span>{" ".join(words[:-1])} <span class="last">{words[-1]}</span></span>'
    return f"<span>{SITE_NAME}</span>"


def nav(current):
    cur = ' aria-current="page"'
    lis = "\n".join(f'      <li><a href="{h}"{cur if h == current else ""}>{l}</a></li>' for h, l in PAGES)
    return f"""<nav class="site" aria-label="Primary">
  <div class="wrap">
    <a class="wordmark" href="index.html">{MARK}{wordmark()}</a>
    <ul>
{lis}
    </ul>
  </div>
</nav>
"""


def foot():
    lis = "\n".join(f'      <li><a href="{h}">{l}</a></li>' for h, l in PAGES)
    return f"""
<footer>
  <div class="wrap">
    <p>I'm {AUTHOR}, and {SITE_NAME} is my project on AI and investing. Research figures come from peer-reviewed studies, cited on each page.</p>
    <ul>
{lis}
    </ul>
    <p class="disclaimer">{SITE_NAME} is a student project. I'm not a registered investment adviser or broker-dealer, and nothing on this site is investment advice or a recommendation to buy or sell any security. Every trade shown happens on a paper account with no real money. Paper-trading and backtested results are hypothetical: they leave out real fees and slippage, and they can't predict future results.</p>
    <p class="disclaimer">Economic data comes from the U.S. Bureau of Labor Statistics and the Federal Reserve Board. Neither agency sponsors or endorses this site.</p>
  </div>
</footer>

</body>
</html>
"""


def sources(keys):
    lis = "\n".join(f"      <li>{SOURCES[k]}</li>" for k in keys)
    return f"""
<section class="refs" id="sources">
  <div class="wrap">
    <h2>Sources</h2>
    <ol>
{lis}
    </ol>
  </div>
</section>
"""


def crumbs(name, path):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE},
        {"@type": "ListItem", "position": 2, "name": name, "item": SITE + path}]}


# ---------------------------------------------------------------- icons
# Lucide icons (ISC license) from tools/icons/.
def svg(body):
    return (f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true">{body}</svg>')


ICONS = {}
for f in glob.glob("tools/icons/*.svg"):
    body = re.search(r"<svg[^>]*>(.*)</svg>", open(f).read(), flags=re.S).group(1)
    ICONS[os.path.basename(f)[:-4]] = svg(re.sub(r"\s+", " ", body).replace(" />", "/>").strip())

# A chart line closing up, on terminal navy.
LINE = ('<rect width="32" height="32" rx="9" fill="#0D1B2E"/>'
        '<path d="M6 22l6-6 5 4 9-10" fill="none" stroke="#6FD3A6" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>'
        '<circle cx="26" cy="10" r="2.2" fill="#FFFFFF"/>')
MARK = f'<svg class="mark" viewBox="0 0 32 32" aria-hidden="true">{LINE}</svg>'


# ---------------------------------------------------------------- blocks
def card_img(name, alt):
    return (f'<img src="images/{name}-720.webp" srcset="images/{name}-480.webp 480w, images/{name}-720.webp 720w" '
            f'sizes="(max-width: 620px) calc(100vw - 40px), (max-width: 1000px) 45vw, 250px" width="720" height="540" alt="{alt}" loading="lazy" decoding="async">')


def wide_banner(name, alt):
    d = ", ".join(f"images/{name}-{w}.webp {w}w" for w in (1000, 1600, 2400))
    m = ", ".join(f"images/{name}-m-{w}.webp {w}w" for w in (600, 900))
    return (f'<picture><source media="(max-width: 860px)" srcset="{m}" sizes="100vw">'
            f'<img src="images/{name}-1600.webp" srcset="{d}" sizes="100vw" width="1600" height="600" alt="{alt}" loading="lazy" decoding="async"></picture>')


def closing_banner(heading, text, href, label, second=None):
    extra = f'<a href="{second[0]}" class="btn ghost-light">{second[1]}</a>' if second else ""
    return f"""
<section class="banner closing-banner">
  {wide_banner("closing", "Three friends laughing together over dinner at a restaurant table")}
  <div class="wrap">
    <div class="banner-text">
      <h2>{heading}</h2>
      <p>{text}</p>
      <div class="btn-row"><a href="{href}" class="btn light">{label}</a>{extra}</div>
    </div>
  </div>
</section>
"""


def points(items):
    return "\n".join(f"""        <li>
          <div class="icon">{ICONS[i]}</div>
          <div><p class="n">{n}</p><h3>{h}</h3><p>{t}</p></div>
        </li>""" for i, n, h, t in items)


def statlist(items):
    return "\n".join(f"""        <li><p class="n">{n}</p><div><h3>{h}</h3><p>{t}</p></div></li>""" for n, h, t in items)


def outcomes(items, mark):
    return "\n".join(f"          <li>{ICONS[mark]}<span>{t}</span></li>" for t in items)


def bars(rows, top):
    return "\n".join(f"""        <div class="barline"><span>{label}</span><div class="track"><span class="bar {cls}" style="width:{val / top * 100:.0f}%">{val:g}%</span></div></div>"""
                     for label, val, cls in rows)


# ---------------------------------------------------------------- latest numbers
# Saved from the BLS Public Data API and the Federal Reserve's FOMC
# statements in tools/data.json. Refresh that file after each report and
# rebuild; every number and chart on the site follows.
DATA = json.load(open("tools/data.json"))
AS_OF = "November 2, 2026"
MON = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
FULL = "January February March April May June July August September October November December".split()


def ym(k, full=False):
    y, m = k.split("-")
    return f"{(FULL if full else MON)[int(m) - 1]} {y}"


def window(series, n=13):
    """The last n months of a series, ending at its newest number."""
    ks = sorted(DATA[series])
    while DATA[series][ks[-1]] is None:
        ks.pop()
    return ks[-n:]


def cpi_yoy():
    c = DATA["CUUR0000SA0"]
    out = []
    for k in window("CUUR0000SA0"):
        a, b = c.get(k), c.get(f"{int(k[:4]) - 1}{k[4:]}")
        out.append((k, None if a is None or b is None else round((a / b - 1) * 100, 1)))
    return out


def cpi_month():
    c = DATA["CUSR0000SA0"]
    a, b = window("CUSR0000SA0", 2)
    return b, round((c[b] / c[a] - 1) * 100, 1)


def payroll_changes():
    p = DATA["CES0000000001"]
    ks = window("CES0000000001")
    return [(k, round(p[k] - p[ks[i - 1]])) for i, k in enumerate(ks) if i]


def series(name):
    return [(k, DATA[name][k]) for k in window(name)]


def spark_line(points, label, step=False):
    """A 12-month line. A month with no data breaks the line."""
    vals = [v for _, v in points if v is not None]
    pad = (max(vals) - min(vals)) * 0.18 or 0.5
    lo, hi = min(vals) - pad, max(vals) + pad
    W, H = 240, 64
    segs, cur = [], []
    for i, (_, v) in enumerate(points):
        if v is None:
            if cur:
                segs.append(cur)
            cur = []
            continue
        x, y = i * W / (len(points) - 1), H - (v - lo) / (hi - lo) * H
        if step and cur:
            cur.append((x, cur[-1][1]))
        cur.append((x, y))
    segs.append(cur)
    lines = "".join('<polyline points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in seg) + '"/>' for seg in segs if seg)
    lx, ly = segs[-1][-1]
    return (f'<svg class="spark" viewBox="-6 -8 {W + 12} {H + 16}" role="img" aria-label="{label}">'
            f'<g fill="none" stroke="currentColor" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round">{lines}</g>'
            f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="4.5" fill="currentColor"/></svg>')


def spark_bars(points, label):
    """Monthly job gains above the line, losses below it."""
    top = max(abs(v) for _, v in points)
    W, H = 240, 64
    mid, bw = H / 2, W / len(points)
    rects = "".join(
        f'<rect class="{"up" if v >= 0 else "down"}" x="{i * bw + bw * 0.18:.1f}" y="{mid - v / top * mid if v >= 0 else mid:.1f}" '
        f'width="{bw * 0.64:.1f}" height="{max(abs(v) / top * mid, 1.5):.1f}" rx="2"/>'
        for i, (_, v) in enumerate(points))
    return (f'<svg class="spark" viewBox="-6 -8 {W + 12} {H + 16}" role="img" aria-label="{label}">'
            f'<line class="axis" x1="0" x2="{W}" y1="{mid}" y2="{mid}"/>{rects}</svg>')


def latest():
    """The newest number from each report, a line of context and a 12-month chart."""
    yoy, jobs, un, fed = cpi_yoy(), payroll_changes(), series("LNS14000000"), series("fedfunds_upper")
    (ck, cv), (jk, jv), (uk, uv) = yoy[-1], jobs[-1], un[-1]
    return {
        "cpi": {"big": f"{cv}%", "series": "CUUR0000SA0", "tape_note": f"12-month, {ym(ck)}",
                "note": f"Prices over the past 12 months, as of {ym(ck, True)}. Up from {yoy[-2][1]}% the month before.",
                "chart": spark_line(yoy, f"12-month inflation from {ym(yoy[0][0])} to {ym(ck)}, ending at {cv}%")},
        "jobs": {"big": f"{jv:+,}K", "series": "CES0000000001", "tape_note": ym(jk),
                 "note": f"Jobs added in {ym(jk, True)}, after {jobs[-2][1]:+,}K the month before.",
                 "chart": spark_bars(jobs, f"Monthly job gains and losses from {ym(jobs[0][0])} to {ym(jk)}")},
        "unemployment": {"big": f"{uv}%", "series": "LNS14000000", "tape_note": ym(uk),
                         "note": f"Share of people looking for work in {ym(uk, True)}. {un[-2][1]}% the month before.",
                         "chart": spark_line(un, f"Unemployment rate from {ym(un[0][0])} to {ym(uk)}, ending at {uv}%")},
        "rates": {"big": "3.75&ndash;4.00%", "series": "FOMC target range", "tape_note": "Held Oct 28",
                  "note": "Held on October 28, after a quarter-point raise in September.",
                  "chart": spark_line(fed, f"Top of the federal funds target range from {ym(fed[0][0])} to {ym(fed[-1][0])}, ending at 4.00%", step=True)},
    }


def report_cards():
    """Home: one card per report with its newest number and the past 12 months."""
    L = latest()
    return "\n".join(f"""      <a class="dcard" href="guide.html#{r['id']}">
        <div class="icon">{ICONS[r['icon']]}</div>
        <h3>{r['name']}</h3>
        <p class="big n">{L[r['id']]['big']}</p>
        <p class="dnote">{L[r['id']]['note']}</p>
        {L[r['id']]['chart']}
        <p class="tag"><code>{L[r['id']]['series']}</code></p>
      </a>""" for r in REPORTS)


def tape():
    """The strip under the home hero: the newest number from each report."""
    L = latest()
    cells = "\n".join(f'    <li><span class="t-name">{r["name"]}</span><span class="t-num n">{L[r["id"]]["big"]}</span><span class="t-note">{L[r["id"]]["tape_note"]}</span></li>'
                      for r in REPORTS)
    return f"""
<section class="tape" aria-label="The newest number from each of the four reports">
  <ul class="wrap">
{cells}
  </ul>
</section>
"""


def sample_read():
    """One read, written from the newest CPI report, the way the AI will write it."""
    k, m = cpi_month()
    yoy = cpi_yoy()
    month = FULL[int(k[5:]) - 1]
    return f"""
<section id="read">
  <div class="wrap split">
    <div>
      <h2>What a read looks like</h2>
      <p class="lead">When a report comes out, the AI pulls the new numbers straight from the agency and writes up what changed in plain English.</p>
      <p>This sample comes from the {ym(k, True)} Consumer Price Index. Every read will also show the trade the AI made on its paper account and the reason it gives.</p>
    </div>
    <article class="readcard" aria-label="Sample read of the {ym(k, True)} Consumer Price Index">
      <header><span class="live" aria-hidden="true"></span><span class="rc-brand">{SITE_NAME}</span><span class="rc-src">CPI &middot; {ym(k)}</span></header>
      <div class="rc-figs">
        <div><p class="n">{m:+}%</p><p>prices in {month}</p></div>
        <div><p class="n">{yoy[-1][1]}%</p><p>over 12 months</p></div>
      </div>
      <p class="rc-body">Prices rose {m}% in {month} and {yoy[-1][1]}% over the past year, up from {yoy[-2][1]}% in {FULL[int(yoy[-2][0][5:]) - 1]}. Faster inflation gives the Federal Reserve a reason to keep interest rates high. It raised its target range in September and held it at 3.75 to 4% on October 28.</p>
      <dl>
        <dt>For your money</dt><dd>Credit cards and other loans tied to rates can stay expensive. Savings accounts can keep paying more.</dd>
        <dt>Next to watch</dt><dd>The Fed's next decision, December 9 at 2:00 p.m. Eastern.</dd>
        <dt>Paper trade</dt><dd>Posted with every read once version one goes live.</dd>
      </dl>
      <footer>Sample read. Paper trading only, with no real money. Not investment advice.</footer>
    </article>
  </div>
</section>
"""


# ---------------------------------------------------------------- home
def index():
    t = f"An AI Agent That Reads the Economic News for Investors | {SITE_NAME}"
    d = ("I'm building an AI that reads the four economic reports that move the market the day they come out "
         "and explains each one in plain English.")
    schema = [page_schema("WebPage", "", t, d, {"about": "AI analysis of economic data for everyday investors"})]
    return head(t, d, "", schema, BANNER_PRELOAD) + nav("index.html") + f"""
<main id="main">

<header class="banner hero-banner">
  <picture>
    <source media="(max-width: 860px)" srcset="images/hero-m-600.webp 600w, images/hero-m-900.webp 900w" sizes="100vw">
    <img src="images/hero-1500.webp" srcset="images/hero-1000.webp 1000w, images/hero-1500.webp 1500w, images/hero-2000.webp 2000w" sizes="70vw" width="1500" height="1000" alt="A man researching at three computer monitors late at night" fetchpriority="high" decoding="async">
  </picture>
  <div class="wrap">
    <div class="banner-text">
      <h1>Deep economics <span>made instant.</span></h1>
      <p>An AI reads the four reports that move the market and explains each one in plain English.</p>
      <div class="btn-row start"><a href="guide.html" class="btn">Download the Free Report Guide</a></div>
    </div>
  </div>
</header>
{tape()}

<section id="problem" class="band">
  <div class="wrap split flip">
    {photo("late-desk", "A man working late at his desk in a dark office, lit by a desk lamp", tall=True)}
    <div>
      <h2>Keeping up with the economy takes hours</h2>
      <p class="lead">Inflation reports, jobs numbers and interest rate decisions arrive every month, spread across many different sources.</p>
      <ul class="points">
{points([("layers", "75% &rarr; 60%", "More information, fewer investors", "In a study of 647 retirement plans, 75% of employees signed up when their plan offered two funds. When it offered 59, about 60% did."),
         ("circle-help", "34%", "Overwhelmed and unsure", "Asked a basic question about spreading out investment risk, 34% of Americans answered &ldquo;do not know.&rdquo;"),
         ("scale", "&minus;3.8 pts", "No one should need an economics degree to manage their own money", "In a study of every trade in Taiwan from 1995 to 1999, individual investors lost 3.8 percentage points a year to trading, while institutions gained 1.5.")])}
      </ul>
      <p class="cite-line">Sources: Sethi-Iyengar, Huberman and Jiang, 2004; Lusardi and Mitchell, 2014; Barber, Lee, Liu and Odean, 2009.</p>
    </div>
  </div>
</section>

<section id="about">
  <div class="wrap split">
    <div>
      <h2>I kept missing the news during class</h2>
      <p>I'm Julian Sassoon, a junior in Georgia. I've spent six years learning how markets work and testing trading strategies. My problem was always time. Big economic reports come out during the school day, and by the time I could look, the market had already moved.</p>
      <p>So I'm building an AI agent that reads the economic data for me. It pulls inflation, interest rate and jobs numbers straight from the Bureau of Labor Statistics and the Federal Reserve, decides what to trade, and explains why. I've already built a trading journal and a position-size calculator with Codex, and I've been experimenting with AI agents since Auto-GPT.</p>
      <div class="btn-row start"><a href="research.html" class="btn ghost">Read the research</a></div>
    </div>
    {portrait("julian", "Julian Sassoon in a blue and green checked shirt, smiling against a white wall")}
  </div>
</section>

<section id="plan" class="band">
  <div class="wrap split flip">
    {photo("letter", "A smiling couple reading a page together at their kitchen table over breakfast")}
    <div>
      <h2>Understand the economic news in three steps</h2>
      <ol class="steps-list">
        <li><div><h3>Download the free report guide</h3><p>One page on the four reports that move the economy: what each one measures, who publishes it and when it comes out.</p></div></li>
        <li><div><h3>Check the AI's read when a report comes out</h3><p>Each week I post what the AI read in the newest reports, what it traded on a paper account with no real money, and why. Paper results are hypothetical and can't predict future returns.</p></div></li>
        <li><div><h3>Know what the news means for your money</h3><p>Spend a few minutes with each report, then decide what it means for your own investments.</p></div></li>
      </ol>
      <div class="btn-row start"><a href="guide.html" class="btn">Download the Free Report Guide</a></div>
    </div>
  </div>
</section>

{sample_read()}
<section id="reports" class="band">
  <div class="wrap">
    <div class="section-head center">
      <h2>Four reports the AI reads first</h2>
      <p>The newest number from each one, with the past 12 months. As of {AS_OF}.</p>
    </div>
    <div class="dcards">
{report_cards()}
    </div>
  </div>
</section>

<section id="stakes" class="after">
  <div class="wrap">
    <div class="section-head center">
      <h2>What changes when you understand the reports</h2>
    </div>
    <div class="stakes-split">
      {photo("cafe-laptop", "Two women smiling as they research something together on a laptop at a cafe")}
      <div class="stakes">
        <div class="stake">
          <h3>When you trade on headlines</h3>
          <ul class="outcomes">
{outcomes(["Big reports come out at 8:30 in the morning, during school and work, and prices move before most people can read them.",
           "The households that traded the most earned 11.4% a year while the market returned 17.9%.",
           "The stocks Robinhood users bought most each day trailed the market by 4.7% over the next 20 trading days."], "x")}
          </ul>
        </div>
        <div class="stake good">
          <h3>When you know what the reports say</h3>
          <ul class="outcomes">
{outcomes(["You know which four reports matter and when each one comes out.",
           "You can see how an AI reads each report and why it makes each paper trade.",
           "You decide what the news means for your own money in a few minutes."], "check")}
          </ul>
        </div>
      </div>
    </div>
    <p class="punch test">I'm testing whether an AI that reads economic data can avoid these mistakes. The paper-trading results will show whether it does.</p>
    <p class="cite-line">Sources: Barber and Odean, Journal of Finance, 2000; Barber, Huang, Odean and Schwarz, Journal of Finance, 2022.</p>
  </div>
</section>
""" + closing_banner("Four economic reports on one page", "What each one measures, who publishes it and when it comes out. Free to download.",
                     "guide.html", "Download the Free Report Guide", ("research.html", "Read the research")) + sources(
        ["choice", "literacy", "taiwan", "hazardous", "robinhood"]) + credits() + "\n</main>\n" + foot()


def credits():
    return """
<section class="refs credits">
  <div class="wrap">
    <p class="cite-line">Photos: Unsplash.</p>
  </div>
</section>
"""


# ---------------------------------------------------------------- report guide
def guide():
    t = f"The Free Economic Report Guide: CPI, Jobs, Unemployment and Interest Rates | {SITE_NAME}"
    d = ("A free one-page guide to the four economic reports investors watch: what each one measures, "
         "who publishes it and when it comes out.")
    schema = [page_schema("WebPage", "guide.html", t, d, {"about": "U.S. economic data releases"}), crumbs("Report Guide", "guide.html")]
    cards = "\n".join(f"""      <article class="report" id="{r['id']}">
        <figure class="card-photo">{card_img(r['photo'], r['alt'])}</figure>
        <div class="report-body">
          <div class="icon">{ICONS[r['icon']]}</div>
          <h3>{r['name']}</h3>
          <p class="series-id"><code>{r['series']}</code></p>
          <p>{r['measures']}</p>
          <dl>
            <dt>Published by</dt><dd>{r['who']}</dd>
            <dt>Comes out</dt><dd>{r['when']}</dd>
            <dt>Why investors watch it</dt><dd>{r['why']}</dd>
          </dl>
        </div>
      </article>""" for r in REPORTS)
    return head(t, d, "guide.html", schema) + nav("guide.html") + f"""
<main id="main">

<header class="page-hero">
  <div class="wrap split">
    <div>
      <h1>The free economic report guide</h1>
      <p class="lede">The four reports my AI reads first, on one page: what each one measures, who publishes it and when it comes out.</p>
      <div class="btn-row start">
        <a href="economic-report-guide.pdf" class="btn" download>Download the PDF</a>
      </div>
    </div>
    {photo("couple", "A man and a woman at a kitchen table looking at a laptop together", eager=True)}
  </div>
</header>

<section class="band" id="guide">
  <div class="wrap">
    <div class="reports">
{cards}
    </div>
    <p class="print-note">Educational only. Nothing here is investment advice or a recommendation to buy or sell any security. Data from the U.S. Bureau of Labor Statistics and the Federal Reserve. {SITE_NAME}, by {AUTHOR}.</p>
  </div>
</section>
""" + closing_banner("Then see what the AI made of them", "Each week I post what the AI read in the newest reports and what it traded on paper.",
                     "updates.html", "Follow the Build Updates") + credits() + "\n</main>\n" + foot()


# ---------------------------------------------------------------- research
def research():
    t = f"How Everyday Investors Handle Financial News: The Research | {SITE_NAME}"
    d = ("What economists have found about investors and information: too many choices, the cost of frequent trading, "
         "and buying whatever grabs attention.")
    schema = [page_schema("Article", "research.html", t, d, {"about": "Individual investors and financial information"}), crumbs("Research", "research.html")]
    return head(t, d, "research.html", schema) + nav("research.html") + f"""
<main id="main">

<header class="page-hero">
  <div class="wrap split">
    <div>
      <h1>What the research says about investors and the news</h1>
      <p class="lede">Before I built anything, I read what economists have found about how everyday investors handle financial information. Here is what the studies show.</p>
    </div>
    {photo("library", "A student studying at a long wooden desk in a library reading room lined with books", eager=True)}
  </div>
</header>

<section id="choice" class="band">
  <div class="wrap split flip">
    {photo("paperwork", "A couple going over papers together at their kitchen table", tall=True)}
    <div>
      <h2>More information, harder decisions</h2>
      <p class="lead">When an investing decision gets more complicated, people tend to put it off or take whatever is picked for them.</p>
      <ul class="statlist">
{statlist([("75% &rarr; 60%", "More funds, fewer savers", "Across 647 retirement plans and almost 800,000 employees, 75% signed up when their plan offered two funds. When it offered 59, about 60% did."),
           ("1.5&ndash;2%", "Every 10 funds", "Each 10 funds a plan added went with a 1.5 to 2 percent drop in sign-ups."),
           ("34%", "&ldquo;Do not know&rdquo;", "Asked a basic question about spreading out investment risk, 34% of Americans answered &ldquo;do not know.&rdquo;"),
           ("20% vs 2%", "Overwhelmed people take the default", "In an experiment, people who knew less about investing took the default choice 20% of the time. People who knew more took it 2% of the time. The authors wrote that people with below-average knowledge &ldquo;are simply overwhelmed by the investment decision.&rdquo;")])}
      </ul>
      <p class="cite-line">Sources: Sethi-Iyengar, Huberman and Jiang, 2004; Lusardi and Mitchell, 2014; Agnew and Szykman, 2005.</p>
    </div>
  </div>
</section>

<section id="trading">
  <div class="wrap split">
    <div>
      <h2>Trading more, earning less</h2>
      <p>Economists followed 66,465 households at a large discount broker from 1991 to 1996. The households that traded the most earned 11.4% a year. The market as a whole returned 17.9%.</p>
      <figure class="chart">
        <h3>Average yearly return, 1991 to 1996</h3>
        <div class="bars">
{bars([("The market", 17.9, "lo"), ("Busiest traders", 11.4, "hi")], 20)}
        </div>
        <p class="cite-line">Source: Barber and Odean, Journal of Finance, 2000.</p>
      </figure>
      <p class="after-chart">A later study used every trade in Taiwan from 1995 to 1999. Individual investors lost 3.8 percentage points a year to trading, while institutions, with their analysts and software, gained 1.5.</p>
      <p class="cite-line">Source: Barber, Lee, Liu and Odean, Review of Financial Studies, 2009.</p>
    </div>
    {photo("late-pair", "Two colleagues going over a report together late at night in a dim office", tall=True)}
  </div>
</section>

<section id="attention" class="band">
  <div class="wrap split flip">
    {photo("night-laptop", "A person working on a laptop at night beside a window over the city lights")}
    <div>
      <h2>Buying whatever grabs attention</h2>
      <p class="lead">Individual investors tend to buy the stocks in the news, and those stocks often do worse afterward.</p>
      <ul class="statlist">
{statlist([("2 to 1", "Buying the buzz", "On days when a stock traded in unusually high volume, individual investors made nearly twice as many purchases of it as sales."),
           ("&minus;4.7%", "The crowd's favorites", "The stocks Robinhood users bought in the biggest numbers each day trailed the market by an average of 4.7% over the next 20 trading days.")])}
      </ul>
      <p class="cite-line">Sources: Barber and Odean, Review of Financial Studies, 2008; Barber, Huang, Odean and Schwarz, Journal of Finance, 2022.</p>
    </div>
  </div>
</section>

<section id="limits">
  <div class="wrap split">
    <div>
      <h2>What these studies can't tell us</h2>
      <p>These studies describe how real investors did, on average, in the past. They don't show that an AI can do better, and they don't say anything about any one investor.</p>
      <p>That's the question my project is testing. Every trade the AI makes happens on a paper account with no real money, and I'll post the results each week, including the weeks it gets wrong. Paper results are hypothetical and can't predict future returns.</p>
      <div class="btn-row start"><a href="updates.html" class="btn ghost">Follow the build updates</a></div>
    </div>
    {photo("laptop-smile", "A man smiling as he reads something on his laptop at a cafe")}
  </div>
</section>
""" + closing_banner("Start with the four reports the AI reads", "One free page on what each report measures and when it comes out.",
                     "guide.html", "Download the Free Report Guide") + sources(
        ["choice", "literacy", "overload", "hazardous", "taiwan", "glitters", "robinhood"]) + credits() + "\n</main>\n" + foot()


# ---------------------------------------------------------------- updates
BUILD = [
    ("Pull the data", "A script downloads inflation, interest rate and jobs data from the Bureau of Labor Statistics and the Federal Reserve as soon as each report comes out."),
    ("Let the AI read it", "An AI agent compares the new numbers with past reports and decides whether to buy, sell or wait."),
    ("Trade on paper", "Each decision goes to a paper-trading account with no real money, along with the AI's reasoning."),
    ("Test it on the past", "The same rules run against years of past data, to see how the strategy would have done."),
]


def updates():
    t = f"Build Updates: An AI Agent That Trades on Economic Data | {SITE_NAME}"
    d = ("Weekly updates on the AI agent I'm building: what it read in each report, "
         "what it traded on paper, and what I changed.")
    schema = [page_schema("WebPage", "updates.html", t, d, {"about": "Building an AI trading agent"}), crumbs("Build Updates", "updates.html")]
    steps = "\n".join(f"""        <li><div><h3>{h}</h3><p>{p}</p></div></li>""" for h, p in BUILD)
    return head(t, d, "updates.html", schema) + nav("updates.html") + f"""
<main id="main">

<header class="page-hero">
  <div class="wrap split">
    <div>
      <h1>Build updates</h1>
      <p class="lede">Every week I post what I built, what the AI read, what it traded on paper and what I changed.</p>
      <div class="btn-row start"><a href="guide.html" class="btn">Download the Free Report Guide</a></div>
    </div>
    {photo("laptop", "A laptop on a wooden desk showing a stock chart with a green price line", eager=True)}
  </div>
</header>

<section class="band">
  <div class="wrap split flip">
    {photo("screens", "A tablet showing a candlestick price chart in front of monitors full of market charts")}
    <div>
      <h2>Version one in four parts</h2>
      <p class="lead">The first version is simple on purpose. Each part will have its own update.</p>
      <ol class="steps-list">
{steps}
      </ol>
    </div>
  </div>
</section>

<section id="log">
  <div class="wrap">
    <div class="section-head center">
      <h2>Weekly updates</h2>
    </div>
    <div class="note">
      <p>The first update goes up in November 2026, when version one starts reading real data.</p>
      <p class="small">Every result posted here comes from a paper account with no real money. Paper and backtested results are hypothetical, leave out real fees and slippage, and can't predict future returns. Nothing here is investment advice.</p>
    </div>
  </div>
</section>
""" + closing_banner("Start with the four reports the AI reads", "One free page on what each report measures and when it comes out.",
                     "guide.html", "Download the Free Report Guide") + credits() + "\n</main>\n" + foot()


# ---------------------------------------------------------------- the PDF guide
# A one-page Letter handout, printed by tools/pdf.cjs. Its own layout: the
# web guide page is not built to be printed.
# Release dates: bls.gov/schedule and federalreserve.gov/monetarypolicy/fomccalendars.htm
CALENDAR = [("Nov 6", "Fri, 8:30 a.m.", "Jobs report for October"),
            ("Nov 10", "Tue, 8:30 a.m.", "Consumer Price Index for October"),
            ("Dec 4", "Fri, 8:30 a.m.", "Jobs report for November"),
            ("Dec 9", "Wed, 2:00 p.m.", "Federal Reserve rate decision"),
            ("Dec 10", "Thu, 8:30 a.m.", "Consumer Price Index for November")]

PRINT_CSS = """
@font-face{font-family:'IBM Plex Sans';font-weight:400;src:url(../fonts/plex-sans-400.woff2) format('woff2')}
@font-face{font-family:'IBM Plex Sans';font-weight:700;src:url(../fonts/plex-sans-700.woff2) format('woff2')}
@font-face{font-family:'IBM Plex Mono';font-weight:500;src:url(../fonts/plex-mono-500.woff2) format('woff2')}
@page{size:Letter;margin:0}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:8.5in;height:11in;background:#fff}
body{font-family:'IBM Plex Sans',sans-serif;color:#0B1118;-webkit-print-color-adjust:exact;print-color-adjust:exact;display:flex;flex-direction:column}
.n{font-family:'IBM Plex Mono',monospace;font-weight:500;letter-spacing:-0.02em}
.top{background:#07090D;color:#EDF1F6;padding:24px 48px 22px}
.brand{display:flex;align-items:center;gap:10px;font-weight:700;font-size:15px}
.brand svg{width:28px;height:28px}
.brand .last{color:#45D19A}
.brand .tag{margin-left:auto;font-weight:400;color:#9AA6B5;font-size:12px}
h1{font-size:35px;line-height:1.05;letter-spacing:-0.03em;margin-top:16px}
h1 span{color:#45D19A}
.top p{color:#9AA6B5;font-size:13px;line-height:1.5;margin-top:8px;max-width:600px}
.body{flex:1;display:flex;flex-direction:column;justify-content:space-evenly;padding:0 48px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.panel{border:1px solid #DDE3EA;border-radius:14px;padding:14px 18px}
.head{display:flex;align-items:center;gap:10px}
.chip{width:28px;height:28px;border-radius:8px;background:#07090D;color:#45D19A;display:grid;place-items:center}
.chip svg{width:16px;height:16px}
h2{font-size:15.5px;letter-spacing:-0.01em}
.now{display:grid;grid-template-columns:auto 1fr;gap:4px 16px;align-items:center;margin-top:9px;padding:9px 0;border-top:1px solid #EEF1F4;border-bottom:1px solid #EEF1F4}
.big{font-size:27px;line-height:1;color:#0B7A50}
.note{grid-column:1/-1;font-size:10.5px;line-height:1.4;color:#5B6675}
.spark{display:block;justify-self:end;width:auto;height:44px;color:#14A06A}
.spark .axis{stroke:#C9D1DA;stroke-width:1}
.spark .up{fill:#14A06A}.spark .down{fill:#E04848}
.what{font-size:11px;line-height:1.42;margin-top:8px}
dl{display:grid;grid-template-columns:76px 1fr;gap:4px 10px;margin-top:8px;font-size:10.5px;line-height:1.36}
dt{font-weight:700}
dd{color:#3E4956}
h3{font-size:13px;margin-bottom:9px}
.cal{display:grid;grid-template-columns:repeat(5,1fr);gap:10px}
.cal li{list-style:none;border-top:3px solid #45D19A;background:#F4F7F9;border-radius:0 0 10px 10px;padding:9px 11px 10px}
.cal .d{font-size:17px;line-height:1.1}
.cal .t{font-size:10px;color:#5B6675;margin-top:2px}
.cal .w{font-size:10.5px;line-height:1.35;font-weight:700;margin-top:6px}
.foot{background:#07090D;color:#9AA6B5;padding:15px 48px 13px;font-size:9.5px;line-height:1.45}
.cta{display:flex;align-items:center;justify-content:space-between;gap:20px;color:#EDF1F6;font-size:13px;font-weight:700;margin-bottom:9px}
.cta .url{font-family:'IBM Plex Mono',monospace;font-weight:500;color:#45D19A;font-size:12.5px}
"""


def guide_print():
    L = latest()
    panels = "\n".join(f"""    <section class="panel">
      <div class="head"><span class="chip">{ICONS[r['icon']]}</span><h2>{r['name']}</h2></div>
      <div class="now"><p class="big n">{L[r['id']]['big']}</p>{L[r['id']]['chart']}<p class="note">{L[r['id']]['note']}</p></div>
      <p class="what">{r['measures']}</p>
      <dl>
        <dt>Published by</dt><dd>{r['who']}</dd>
        <dt>Comes out</dt><dd>{r['when']}</dd>
        <dt>Your money</dt><dd>{r['why']}</dd>
      </dl>
    </section>""" for r in REPORTS)
    cal = "\n".join(f'      <li><p class="d n">{d}</p><p class="t">{t} Eastern</p><p class="w">{w}</p></li>' for d, t, w in CALENDAR)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="robots" content="noindex,nofollow">
<title>The Free Economic Report Guide | {SITE_NAME}</title>
<style>{PRINT_CSS}</style>
</head>
<body>
<header class="top">
  <div class="brand"><svg viewBox="0 0 32 32" aria-hidden="true">{LINE}</svg>{wordmark()}<span class="tag">The Free Economic Report Guide</span></div>
  <h1>The four reports that <span>move the market</span></h1>
  <p>What each one measures, who publishes it, when it comes out and where it stands now. Numbers as of {AS_OF}, straight from the Bureau of Labor Statistics and the Federal Reserve.</p>
</header>
<main class="body">
  <div class="grid">
{panels}
  </div>
  <section>
    <h3>Next on the calendar</h3>
    <ul class="cal">
{cal}
    </ul>
  </section>
</main>
<footer class="foot">
  <div class="cta"><span>Read the AI's plain-English take on each report the day it comes out.</span><span class="url">odyssey-jotun.github.io/macro-signal</span></div>
  <p>{SITE_NAME} is a student project by Julian Sassoon. Educational only: nothing here is investment advice or a recommendation to buy or sell any security. The AI trades a paper account with no real money.</p>
</footer>
</body>
</html>
"""


def sitemap():
    urls = "\n".join(f"  <url><loc>{SITE}{'' if h == 'index.html' else h}</loc><lastmod>{TODAY}</lastmod></url>" for h, _ in PAGES)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n'


if __name__ == "__main__":
    for name, fn in {"index.html": index, "guide.html": guide, "research.html": research, "updates.html": updates}.items():
        with open(name, "w") as f:
            f.write(fn())
        print("wrote", name)
    with open("tools/guide-print.html", "w") as f:
        f.write(guide_print())
    with open("sitemap.xml", "w") as f:
        f.write(sitemap())
    with open("robots.txt", "w") as f:
        allow = "Allow: /" if ROBOTS.startswith("index") else "Disallow: /"
        f.write(f"User-agent: *\n{allow}\n\nSitemap: {SITE}sitemap.xml\n")
    with open("favicon.svg", "w") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">{LINE}</svg>\n')
