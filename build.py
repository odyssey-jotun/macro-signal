#!/usr/bin/env python3
"""Builds every page of the site, plus sitemap.xml, robots.txt and favicon.svg.

Run: python3 build.py
The site name lives in SITE_NAME below. Change it there, rebuild, and every
page title, wordmark, footer and JSON-LD block follows. Copy and facts live
in this file too, so a correction is made once.
"""
import json
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
    "robinhood": "Barber, Brad M., Xing Huang, Terrance Odean and Christopher Schwarz. <em>Attention-Induced Trading and Returns: Evidence from Robinhood Users.</em> Journal of Finance 77, no. 6 (2022): 3141-3190.",
}

# ---------------------------------------------------------------- the data
# The economic releases the agent reads first, by the series IDs their
# publishers use: the Bureau of Labor Statistics and the Federal Reserve
# Board. Both are public-domain U.S. government data. FRED is not used: its
# terms forbid using FRED content to develop software or AI.
SERIES = [
    {"id": "CUSR0000SA0", "icon": "cart", "name": "Inflation", "text": "The Consumer Price Index, from the Bureau of Labor Statistics."},
    {"id": "RIFSPFF_N.M", "icon": "bank", "name": "Interest rates", "text": "The federal funds rate, from the Federal Reserve Board."},
    {"id": "CES0000000001", "icon": "people", "name": "Jobs", "text": "Payroll jobs from the monthly jobs report."},
    {"id": "LNS14000000", "icon": "chart", "name": "Unemployment", "text": "The share of workers looking for a job."},
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


def photo(name, alt, eager=False):
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<figure class="photo"><img src="images/{name}-900.webp" srcset="images/{name}-600.webp 600w, images/{name}-900.webp 900w" '
            f'sizes="(max-width: 860px) calc(100vw - 40px), 520px" width="900" height="675" alt="{alt}" {load} decoding="async"></figure>')


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
              "description": "An AI agent that reads inflation, interest rate and jobs data and explains every paper trade it makes.",
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
<meta property="og:image:alt" content="The economy, read for you. An AI agent that reads the economic news.">
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


PAGES = [("index.html", "Home"), ("updates.html", "Build Updates")]


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


def cta(heading, text, href, label):
    return f"""
<section class="closing">
  <div class="wrap">
    <h2>{heading}</h2>
    <p>{text}</p>
    <div class="btn-row"><a href="{href}" class="btn">{label}</a></div>
  </div>
</section>
"""


# ---------------------------------------------------------------- icons
def svg(body, sw="2.6"):
    return (f'<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="{sw}" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true">{body}</svg>')


# A chart line closing up, on terminal navy.
LINE = ('<rect width="32" height="32" rx="9" fill="#0D1B2E"/>'
        '<path d="M6 22l6-6 5 4 9-10" fill="none" stroke="#6FD3A6" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>'
        '<circle cx="26" cy="10" r="2.2" fill="#FFFFFF"/>')
MARK = f'<svg class="mark" viewBox="0 0 32 32" aria-hidden="true">{LINE}</svg>'
ICONS = {
    "stack": svg('<rect x="8" y="8" width="26" height="9" rx="2"/><rect x="11" y="20" width="26" height="9" rx="2"/><rect x="14" y="32" width="26" height="9" rx="2"/>'),
    "fog": svg('<circle cx="24" cy="24" r="17"/><path d="M19 19a5 5 0 1 1 7 4.6c-1.3.6-2 1.6-2 3V28"/><path d="M24 34v.5"/>'),
    "scale": svg('<path d="M24 7v33M15 41h18M9 13h30"/><path d="M9 13L4 25h10zM39 13l-5 12h10z"/><path d="M4 25c0 3 2 5 5 5s5-2 5-5M34 25c0 3 2 5 5 5s5-2 5-5"/>'),
    "cart": svg('<path d="M5 8h6l4 22h22l4-15H14"/><circle cx="18" cy="38" r="3"/><circle cx="34" cy="38" r="3"/>'),
    "bank": svg('<path d="M6 18L24 7l18 11z"/><path d="M10 22v13M19 22v13M29 22v13M38 22v13M6 40h36"/>'),
    "people": svg('<circle cx="17" cy="16" r="6"/><circle cx="33" cy="18" r="5"/><path d="M6 40c0-7 5-12 11-12s11 5 11 12M29 40c0-5 2-10 8-10 4 0 6 4 6 10"/>'),
    "chart": svg('<path d="M7 7v34h34"/><path d="M13 31l8-9 7 5 11-14"/>'),
    "headline": svg('<rect x="6" y="9" width="36" height="30" rx="3"/><path d="M12 16h24M12 23h11M12 30h11M28 23h8v7h-8z"/>'),
    "drop": svg('<path d="M7 12l12 14 8-7 14 17"/><path d="M33 36h8v-8"/>'),
}


# ---------------------------------------------------------------- home
def index():
    t = f"An AI Agent That Reads the Economic News for Investors | {SITE_NAME}"
    d = ("I'm building an AI agent that reads inflation, interest rate and jobs data, "
         "makes paper trades and explains the reasoning behind each one.")
    schema = [page_schema("WebPage", "", t, d, {"about": "AI analysis of economic data for everyday investors"})]
    series = "\n".join(f"""      <li>
        <span class="sicon">{ICONS[s['icon']]}</span>
        <code>{s['id']}</code>
        <h3>{s['name']}</h3>
        <p>{s['text']}</p>
      </li>""" for s in SERIES)
    return head(t, d, "", schema, BANNER_PRELOAD) + nav("index.html") + f"""
<main id="main">

<header class="banner">
  <picture>
    <source media="(max-width: 860px)" srcset="images/banner-m-600.webp 600w, images/banner-m-900.webp 900w" sizes="100vw">
    <img src="images/banner-1600.webp" srcset="images/banner-1000.webp 1000w, images/banner-1600.webp 1600w, images/banner-2400.webp 2400w" sizes="100vw" width="1600" height="800" alt="A smiling man in his kitchen holding a coffee mug and reading his phone" fetchpriority="high" decoding="async">
  </picture>
  <div class="wrap">
    <div class="banner-text">
      <h1>The economy, <span>read for you.</span></h1>
      <div class="btn-row">
        <a href="updates.html" class="btn light">Follow the Build</a>
      </div>
    </div>
  </div>
</header>

<section id="problem" class="band">
  <div class="wrap">
    <div class="section-head center">
      <h2>Keeping up with the economy takes hours</h2>
      <p>Inflation reports, jobs numbers and interest rate decisions arrive every month, spread across many different sources.</p>
    </div>
    <div class="readouts">
      <div class="readout">
        <div class="icon">{ICONS['stack']}</div>
        <p class="stat">75% &rarr; 60%</p>
        <h3>More information, fewer investors</h3>
        <p>In a study of 647 retirement plans, 75% of employees signed up when their plan offered two funds. When it offered 59, about 60% did.</p>
      </div>
      <div class="readout">
        <div class="icon">{ICONS['fog']}</div>
        <p class="stat">34%</p>
        <h3>Overwhelmed and unsure</h3>
        <p>Asked a basic question about spreading out investment risk, 34% of Americans answered "do not know." Researchers found that people who knew less about investing were simply overwhelmed by the decision.</p>
      </div>
      <div class="readout">
        <div class="icon">{ICONS['scale']}</div>
        <p class="stat">&minus;3.8 pts</p>
        <h3>No one should need an economics degree to manage their own money</h3>
        <p>Professionals have analysts and software watching the market all day. In a study of every trade in Taiwan from 1995 to 1999, individual investors lost 3.8 percentage points a year to trading, while institutions gained 1.5.</p>
      </div>
    </div>
    <p class="cite-line" style="text-align:center">Sources: Sethi-Iyengar, Huberman and Jiang, 2004; Lusardi and Mitchell, Journal of Economic Literature, 2014; Agnew and Szykman, Journal of Behavioral Finance, 2005; Barber, Lee, Liu and Odean, Review of Financial Studies, 2009.</p>
  </div>
</section>

<section id="about">
  <div class="wrap split flip">
    {portrait("julian", "Julian Sassoon in a blue and green checked shirt, smiling against a white wall")}
    <div>
      <h2>I kept missing the news during class</h2>
      <p>I'm Julian Sassoon, a junior in Georgia. I've spent six years learning how markets work and testing trading strategies. My problem was always time. Big economic reports come out during the school day, and by the time I could look, the market had already moved.</p>
      <p>So I'm building an AI agent that reads the economic data for me. It pulls inflation, interest rate and jobs numbers straight from the Bureau of Labor Statistics and the Federal Reserve, decides what to trade, and explains why. I've already built a trading journal and a position-size calculator with Codex, and I've been experimenting with AI agents since Auto-GPT.</p>
    </div>
  </div>
</section>

<section id="plan" class="band">
  <div class="wrap">
    <div class="section-head center">
      <h2>See how an AI investor thinks in three steps</h2>
      <p>Every trade happens on a practice account first.</p>
    </div>
    <ol class="timeline">
      <li>
        <h3>Follow the weekly build updates</h3>
        <p>Each week I post what I built, what the AI read and what it decided.</p>
      </li>
      <li>
        <h3>Watch the paper-trading results</h3>
        <p>The AI trades a practice account with no real money, and every result goes on the site, wins and losses. Paper results are hypothetical and can't predict future returns.</p>
      </li>
      <li>
        <h3>Try the free demo</h3>
        <p>When the demo opens, watch the AI read a jobs report or an inflation release and decide what to do.</p>
      </li>
    </ol>
    <p class="punch">I'll show the reasoning behind every trade the AI makes, so you can judge each one.</p>
    <div class="btn-row">
      <a href="updates.html" class="btn">Follow the Build</a>
    </div>
  </div>
</section>

<section id="data">
  <div class="wrap">
    <div class="section-head center">
      <h2>Four reports the AI reads first</h2>
      <p>Each one comes straight from the agency that publishes it, by its series ID.</p>
    </div>
    <div class="terminal">
      <p class="terminal-bar" aria-hidden="true"><span></span><span></span><span></span>api.bls.gov &middot; federalreserve.gov</p>
      <ul class="series">
{series}
      </ul>
    </div>
  </div>
</section>

<section id="success" class="band">
  <div class="wrap split">
    <div>
      <h2>Know what the news means for your money</h2>
      <p>You'll see how an AI reads each report and why it trades, so you can decide what the news means for your own money. And you'll spend less time reading financial news.</p>
    </div>
    {photo("phone", "A woman reading her phone at a cafe table beside a coffee cup and a leather notebook")}
  </div>
</section>

<section id="stakes" class="after">
  <div class="wrap">
    <div class="section-head center">
      <h2>Trading on headlines costs money</h2>
      <p>Investors who react to whatever grabs their attention tend to trail the market.</p>
    </div>
    <div class="facts">
      <div class="fact">
        <div class="icon">{ICONS['drop']}</div>
        <h3>The busiest traders earned less</h3>
        <div class="bars" role="img" aria-label="Average yearly return, 1991 to 1996: the market 17.9%, the households with the heaviest trading 11.4%">
          <div class="bar"><span class="label">The market</span><span class="fill" style="width:100%"></span><span class="val">17.9%</span></div>
          <div class="bar busy"><span class="label">Busiest traders</span><span class="fill" style="width:63.7%"></span><span class="val">11.4%</span></div>
        </div>
        <p>Among 66,465 households at a discount broker from 1991 to 1996, the households with the heaviest trading earned 11.4% a year. The market returned 17.9%.</p>
      </div>
      <div class="fact">
        <div class="icon">{ICONS['headline']}</div>
        <p class="stat">&minus;4.7%</p>
        <h3>The crowd's favorite stocks fell behind</h3>
        <p>The stocks Robinhood users bought in the biggest numbers each day trailed the market by an average of 4.7% over the next 20 trading days.</p>
      </div>
    </div>
    <p class="punch test">I'm testing whether an AI that reads economic data can avoid these mistakes. The paper-trading results will show whether it does.</p>
    <p class="cite-line">Sources: Barber and Odean, Journal of Finance, 2000; Barber, Huang, Odean and Schwarz, Journal of Finance, 2022.</p>
  </div>
</section>
""" + cta("Watch an AI read the jobs report", "Weekly updates on what the AI read, what it traded on paper and why.",
          "updates.html", "Follow the Build") + sources(["choice", "literacy", "overload", "taiwan", "hazardous", "robinhood"]) + "\n</main>\n" + foot()


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
    schema = [page_schema("WebPage", "updates.html", t, d, {"about": "Building an AI trading agent"}),
              {"@type": "BreadcrumbList", "itemListElement": [
                  {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE},
                  {"@type": "ListItem", "position": 2, "name": "Build Updates", "item": SITE + "updates.html"}]}]
    steps = "\n".join(f"""      <li>
        <h3>{h}</h3>
        <p>{p}</p>
      </li>""" for h, p in BUILD)
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
  <div class="wrap">
    <div class="section-head center">
      <h2>Version one in four parts</h2>
      <p>The first version is simple on purpose. Each part will have its own update.</p>
    </div>
    <ol class="build">
{steps}
    </ol>
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
""" + cta("Four reports, one AI, no real money", "See what the AI reads first, and why I'm building it.",
          "index.html#data", "See the Data") + "\n</main>\n" + foot()


def sitemap():
    urls = "\n".join(f"  <url><loc>{SITE}{'' if h == 'index.html' else h}</loc><lastmod>{TODAY}</lastmod></url>" for h, _ in PAGES)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n'


if __name__ == "__main__":
    for name, fn in {"index.html": index, "updates.html": updates}.items():
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
