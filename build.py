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


BANNER_PRELOAD = ('<link rel="preload" as="image" type="image/webp" media="(min-width: 861px)" href="images/banner-1600.webp" '
                  'imagesrcset="images/banner-1000.webp 1000w, images/banner-1600.webp 1600w, images/banner-2400.webp 2400w" imagesizes="100vw" fetchpriority="high">\n'
                  '<link rel="preload" as="image" type="image/webp" media="(max-width: 860px)" href="images/banner-m-900.webp" '
                  'imagesrcset="images/banner-m-600.webp 600w, images/banner-m-900.webp 900w" imagesizes="100vw" fetchpriority="high">\n')


PERSON = {
    "@type": "Person", "@id": SITE + "#julian", "name": AUTHOR,
    "description": f"High school junior in Georgia building {SITE_NAME}, an AI agent that reads U.S. economic data and paper trades on it.",
}


def head(title, desc, path="", schema=None, pre=""):
    url = SITE + path
    graph = [{"@type": "WebSite", "@id": SITE + "#site", "url": SITE, "name": SITE_NAME,
              "description": "Economic news made simple. An AI that reads the four economic reports that move the market and explains each one in plain English.",
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
<meta property="og:image:alt" content="Economic news made simple. An AI that explains the economic reports in plain English.">
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


def report_cards():
    """Home: one photo card per report, linking to its spot in the guide."""
    return "\n".join(f"""      <a class="pcard" href="guide.html#{r['id']}">
        <figure class="card-photo">{card_img(r['photo'], r['alt'])}</figure>
        <div class="pcard-body"><p class="tag"><code>{r['series']}</code></p><h3>{r['name']}</h3><p>{r['short']}</p></div>
      </a>""" for r in REPORTS)


# ---------------------------------------------------------------- home
def index():
    t = f"An AI Agent That Reads the Economic News for Investors | {SITE_NAME}"
    d = ("I'm building an AI that reads the four economic reports that move the market the day they come out "
         "and explains each one in plain English.")
    schema = [page_schema("WebPage", "", t, d, {"about": "AI analysis of economic data for everyday investors"})]
    return head(t, d, "", schema, BANNER_PRELOAD) + nav("index.html") + f"""
<main id="main">

<header class="banner">
  <picture>
    <source media="(max-width: 860px)" srcset="images/banner-m-600.webp 600w, images/banner-m-900.webp 900w" sizes="100vw">
    <img src="images/banner-1600.webp" srcset="images/banner-1000.webp 1000w, images/banner-1600.webp 1600w, images/banner-2400.webp 2400w" sizes="100vw" width="1600" height="800" alt="A smiling man in his kitchen holding a coffee mug and reading his phone" fetchpriority="high" decoding="async">
  </picture>
  <div class="wrap">
    <div class="banner-text">
      <h1>Economic news <span>made simple.</span></h1>
      <div class="btn-row">
        <a href="guide.html" class="btn light">Download the Free Report Guide</a>
      </div>
    </div>
  </div>
</header>

<section id="problem" class="band">
  <div class="wrap split flip">
    {photo("newspaper", "A man at a cafe table reading the business section of the newspaper, hand on his chin", tall=True)}
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
  <div class="wrap split flip">
    {portrait("julian", "Julian Sassoon in a blue and green checked shirt, smiling against a white wall")}
    <div>
      <h2>I kept missing the news during class</h2>
      <p>I'm Julian Sassoon, a junior in Georgia. I've spent six years learning how markets work and testing trading strategies. My problem was always time. Big economic reports come out during the school day, and by the time I could look, the market had already moved.</p>
      <p>So I'm building an AI agent that reads the economic data for me. It pulls inflation, interest rate and jobs numbers straight from the Bureau of Labor Statistics and the Federal Reserve, decides what to trade, and explains why. I've already built a trading journal and a position-size calculator with Codex, and I've been experimenting with AI agents since Auto-GPT.</p>
      <div class="btn-row start"><a href="research.html" class="btn ghost">Read the research</a></div>
    </div>
  </div>
</section>

<section id="plan" class="band">
  <div class="wrap split">
    <div>
      <h2>Understand the economic news in three steps</h2>
      <ol class="steps-list">
        <li><div><h3>Download the free report guide</h3><p>One page on the four reports that move the economy: what each one measures, who publishes it and when it comes out.</p></div></li>
        <li><div><h3>Check the AI's read when a report comes out</h3><p>Each week I post what the AI read in the newest reports, what it traded on a paper account with no real money, and why. Paper results are hypothetical and can't predict future returns.</p></div></li>
        <li><div><h3>Know what the news means for your money</h3><p>Spend a few minutes with each report, then decide what it means for your own investments.</p></div></li>
      </ol>
      <div class="btn-row start"><a href="guide.html" class="btn">Download the Free Report Guide</a></div>
    </div>
    {photo("letter", "A smiling couple reading a page together at their kitchen table over breakfast")}
  </div>
</section>

<section id="reports">
  <div class="wrap">
    <div class="section-head center">
      <h2>Four reports the AI reads first</h2>
      <p>Each one comes straight from the agency that publishes it, by its series ID.</p>
    </div>
    <div class="pcards four">
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
      {photo("phone", "A woman reading her phone at a cafe table beside a coffee cup and a leather notebook")}
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
    {photo("chart-phone", "A hand holding up a phone showing a stock chart in front of a large screen of price charts", tall=True)}
  </div>
</section>

<section id="attention" class="band">
  <div class="wrap split flip">
    {photo("students-phones", "Two students smiling at a phone together at a desk in a lecture hall")}
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
    {photo("friends-phone", "A man and a woman laughing together as they look at a phone")}
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


def sitemap():
    urls = "\n".join(f"  <url><loc>{SITE}{'' if h == 'index.html' else h}</loc><lastmod>{TODAY}</lastmod></url>" for h, _ in PAGES)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n'


if __name__ == "__main__":
    for name, fn in {"index.html": index, "guide.html": guide, "research.html": research, "updates.html": updates}.items():
        with open(name, "w") as f:
            f.write(fn())
        print("wrote", name)
    with open("sitemap.xml", "w") as f:
        f.write(sitemap())
    with open("robots.txt", "w") as f:
        allow = "Allow: /" if ROBOTS.startswith("index") else "Disallow: /"
        f.write(f"User-agent: *\n{allow}\n\nSitemap: {SITE}sitemap.xml\n")
    with open("favicon.svg", "w") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">{LINE}</svg>\n')
