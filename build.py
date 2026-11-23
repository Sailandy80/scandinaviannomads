#!/usr/bin/env python3
"""Static site generator for scandinaviannomads.com.

Content lives in content/ (Markdown + YAML front matter).
Run:  python3 build.py   -> writes the finished site to dist/
"""
import hashlib, html, math, random, re, shutil, datetime as dt
from pathlib import Path

import markdown, yaml

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
DIST = ROOT / "dist"
SITE = yaml.safe_load((CONTENT / "site.yaml").read_text(encoding="utf-8"))
BASE = SITE["url"].rstrip("/")
ASSET_V = ""  # filled in after assets are hashed

REGIONS = ["Scandinavia", "Europe", "Asia", "Americas", "Africa & Middle East"]
TIP_CATEGORIES = ["Flights & Points", "Hotels", "Food & Dining", "Planning", "Gear"]
DISCLOSURE_LINE = ("Some links are affiliate links. If you book through them we may earn a small "
                   "commission at no extra cost to you. We only recommend what we would use ourselves.")

esc = html.escape


# ---------------------------------------------------------------- content

def load(folder):
    items = []
    for f in sorted((CONTENT / folder).glob("*.md")):
        raw = f.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
        meta = yaml.safe_load(m.group(1)) if m else {}
        body = m.group(2) if m else raw
        meta["slug"] = meta.get("slug") or f.stem
        meta["body_md"] = body
        meta["html"] = markdown.markdown(body, extensions=["extra", "sane_lists"])
        pub = meta.get("published")
        meta["published"] = pub if isinstance(pub, dt.date) else dt.date.fromisoformat(str(pub))
        if meta.get("draft"):
            continue
        items.append(meta)
    items.sort(key=lambda x: (x["published"], x["slug"]), reverse=True)
    return items


DESTS = load("destinations")
TIPS = load("tips")
NEWS = load("news")


# ---------------------------------------------------------------- art

def art_svg(slug, art, w=1200, h=760, title=""):
    """Original, generated landscape poster (no third-party images)."""
    art = art or {}
    rnd = random.Random(int(hashlib.md5(slug.encode()).hexdigest(), 16))
    sky = art.get("sky", "#DCE4EA")
    sea = art.get("sea", "#0F2A3D")
    lands = art.get("land", ["#3D5A6C", "#2A4556", "#173041"])
    sun = art.get("sun", "#E8DCC8")
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid slice" role="img" aria-label="{esc(title)}">',
             f'<defs><linearGradient id="s{slug}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{sky}"/><stop offset="1" stop-color="#FBF8F3"/></linearGradient></defs>',
             f'<rect width="{w}" height="{h}" fill="url(#s{slug})"/>']
    sx, sy, sr = rnd.randint(int(w*.55), int(w*.8)), rnd.randint(int(h*.15), int(h*.3)), rnd.randint(55, 90)
    parts.append(f'<circle cx="{sx}" cy="{sy}" r="{sr}" fill="{sun}" opacity=".9"/>')
    n = len(lands)
    for i, col in enumerate(lands):
        base = h * (0.48 + 0.12 * i)
        amp = h * (0.26 - 0.06 * i)
        pts, x = [(0, h)], 0
        while x <= w:
            y = base - abs(math.sin(x / (w / (2.2 + i)) + rnd.random())) * amp * rnd.uniform(.55, 1)
            pts.append((x, y))
            x += rnd.randint(40, 110)
        pts += [(w, base - amp * .3), (w, h)]
        d = "M" + " L".join(f"{px:.0f},{py:.0f}" for px, py in pts) + " Z"
        parts.append(f'<path d="{d}" fill="{col}" opacity="{0.92 if i < n-1 else 1}"/>')
    wy = h * 0.86
    parts.append(f'<rect y="{wy:.0f}" width="{w}" height="{h-wy:.0f}" fill="{sea}"/>')
    for k in range(6):
        y = wy + 10 + k * 14
        x1 = rnd.randint(0, w // 2)
        parts.append(f'<line x1="{x1}" y1="{y:.0f}" x2="{x1 + rnd.randint(60, 220)}" y2="{y:.0f}" stroke="#FBF8F3" stroke-opacity=".25" stroke-width="2"/>')
    parts.append("</svg>")
    return "".join(parts)


# ---------------------------------------------------------------- layout

NAV = [("Destinations", "/destinations/"), ("Travel News", "/news/"), ("Tips", "/tips/"),
       ("Toolkit", "/toolkit/"), ("About", "/about/"), ("Contact", "/contact/")]


def page(path, title, desc, body, active="", og_image="/assets/og.png", kind="website"):
    full_title = f"{title} | {SITE['name']}" if title != SITE["name"] else f"{SITE['name']} | {SITE['tagline']}"
    canonical = BASE + path
    nav = "".join(f'<a href="{u}"{" aria-current=\"page\"" if active == n else ""}>{n}</a>' for n, u in NAV)
    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="{kind}">
<meta property="og:site_name" content="{esc(SITE['name'])}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{BASE}{og_image}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css?v={ASSET_V}">
<link rel="alternate" type="application/rss+xml" title="{esc(SITE['name'])} – Travel News" href="/feed.xml">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="logo" href="/"><span class="logo-mark" aria-hidden="true">◆</span> Scandinavian Nomads</a>
    <button class="menu-btn" aria-expanded="false" aria-controls="nav">Menu</button>
    <nav id="nav" class="nav" aria-label="Main">{nav}</nav>
  </div>
</header>
<main id="main">
{body}
</main>
{newsletter_block() if path not in ("/contact/",) else ""}
<footer class="site-footer">
  <div class="wrap footer-grid">
    <div>
      <p class="logo">Scandinavian Nomads</p>
      <p class="muted">Luxury travel, without the luxury price tag. Guides, tips and weekly travel news from a Norwegian traveller who has visited 90+ countries.</p>
    </div>
    <nav aria-label="Footer">{nav}</nav>
    <div class="footer-small">
      <a href="/disclosure/">Affiliate disclosure</a>
      <a href="/privacy/">Privacy</a>
      <a href="/feed.xml">RSS</a>
      <a href="mailto:{SITE['email']}">{SITE['email']}</a>
    </div>
  </div>
  <div class="wrap copyright">© {SITE['year']} Scandinavian Nomads</div>
</footer>
<script src="/assets/main.js?v={ASSET_V}" defer></script>
</body>
</html>
"""
    out = DIST / path.strip("/") / "index.html" if path.endswith("/") else DIST / path.lstrip("/")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    return path


def newsletter_block(inline=False):
    return f"""<section class="newsletter{' inline' if inline else ''}" id="newsletter">
  <div class="wrap newsletter-inner">
    <div>
      <p class="eyebrow">The good travel letter</p>
      <h2>Weekly travel news and budget-luxury finds</h2>
      <p class="muted">One short email a week. No spam, unsubscribe any time.</p>
    </div>
    <form class="subscribe" action="/subscribe.php" method="post">
      <label class="sr" for="nl-email{'-i' if inline else ''}">Email address</label>
      <input id="nl-email{'-i' if inline else ''}" type="email" name="email" placeholder="your@email.com" required>
      <input type="text" name="website" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
      <button type="submit">Count me in</button>
      <p class="fineprint">By subscribing you agree to our <a href="/privacy/">privacy policy</a>.</p>
    </form>
  </div>
</section>"""


def fmt_date(d):
    return d.strftime("%-d %B %Y")


def sponsored_badge(item):
    return '<span class="badge sponsored">Sponsored</span>' if item.get("sponsored") else ""


# ---------------------------------------------------------------- components

def dest_card(d, big=False):
    return f"""<a class="card dest-card{' big' if big else ''}" href="/destinations/{d['slug']}/" data-region="{esc(d['region'])}">
  <div class="card-art">{art_svg(d['slug'], d.get('art'), title=d['title'])}<span class="score" title="Budget luxury score">{d['score']}</span></div>
  <div class="card-body">
    <p class="eyebrow">{esc(d['country'])} · {esc(d['region'])}</p>
    <h3>{esc(d['title'])}</h3>
    <p>{esc(d['tagline'])}</p>
  </div>
</a>"""


def tip_card(t):
    return f"""<a class="card tip-card" href="/tips/{t['slug']}/">
  <div class="card-body">
    <p class="eyebrow">{esc(t['category'])}</p>
    <h3>{esc(t['title'])}</h3>
    <p>{esc(t['summary'])}</p>
    <span class="more">Read the guide →</span>
  </div>
</a>"""


def news_items_html(items, limit=None):
    out = []
    for it in (items[:limit] if limit else items):
        src = ""
        if it.get("url"):
            src = f'<a class="source" href="{esc(it["url"])}" target="_blank" rel="noopener">Source: {esc(it.get("source", "link"))} ↗</a>'
        out.append(f"""<article class="news-item">
  <h3>{esc(it['headline'])}</h3>
  <p>{esc(it['summary'])}</p>
  {f'<p class="impact"><strong>What it means for you:</strong> {esc(it["impact"])}</p>' if it.get('impact') else ''}
  {src}
</article>""")
    return "".join(out)


def affiliate_box(d):
    L = d.get("links") or {}
    rows = []
    def btn(key, label):
        if L.get(key):
            rows.append(f'<a class="btn" href="{esc(L[key])}" target="_blank" rel="sponsored nofollow noopener">{esc(label)}</a>')
    btn("hotel", L.get("hotel_label") or f"Find hotels in {d['title']}")
    btn("activities", L.get("activities_label") or f"Tours and activities in {d['title']}")
    btn("transfer", L.get("transfer_label") or "Airport transfers and car hire")
    btn("flights", L.get("flights_label") or f"Flights to {d['title']}")
    btn("insurance", L.get("insurance_label") or "Travel insurance")
    if not rows:
        return ""
    return f"""<aside class="book-box">
  <p class="disclosure-line">{DISCLOSURE_LINE} <a href="/disclosure/">Learn more</a>.</p>
  <h2>Book it the smart way</h2>
  <div class="btn-row">{''.join(rows)}</div>
</aside>"""


def products_box(t):
    prods = t.get("products") or []
    if not prods:
        return ""
    lis = "".join(f'<li><a href="{esc(p["url"])}" target="_blank" rel="sponsored nofollow noopener">{esc(p["name"])}</a> – {esc(p.get("reason", ""))}</li>' for p in prods)
    return f"""<aside class="book-box">
  <p class="disclosure-line">{DISCLOSURE_LINE} <a href="/disclosure/">Learn more</a>.</p>
  <h2>What we recommend</h2><ul>{lis}</ul>
</aside>"""


def inline_hotel_button(d):
    L = d.get("links") or {}
    if not L.get("hotel"):
        return ""
    return (f'<p class="inline-cta"><a class="btn small" href="{esc(L["hotel"])}" target="_blank" '
            f'rel="sponsored nofollow noopener">{esc(L.get("hotel_label") or "Check hotel prices")} →</a> '
            f'<span class="muted">(affiliate link)</span></p>')


# ---------------------------------------------------------------- pages

def build_home():
    featured = next((d for d in DESTS if d.get("featured")), DESTS[0])
    real_news = [n for n in NEWS if not n.get("placeholder")]
    if real_news:
        latest = real_news[0]
        news_html = f"""<p class="muted">Week {latest['week']}, {latest['year']}</p>
<div class="news-grid">{news_items_html(latest.get('items') or [], 3)}</div>
<a class="more" href="/news/{latest['slug']}/">Read the full roundup →</a>"""
    else:
        news_html = '<div class="empty-note"><p><strong>Coming soon.</strong> The first weekly roundup lands on a Monday morning. Subscribe below to get it by email.</p></div>'
    body = f"""
<section class="hero">
  <div class="hero-art">{art_svg('lofoten-hero', next((d.get('art') for d in DESTS if d['slug']=='lofoten'), None), 1600, 900, 'Lofoten, Norway')}</div>
  <div class="wrap hero-inner">
    <p class="eyebrow light">Budget luxury travel</p>
    <h1>Luxury travel, without the luxury price tag</h1>
    <p class="lead">Boutique stays, business class on points and long lunches at great restaurants. Smart guides from a Norwegian who has explored 90+ countries.</p>
    <div class="btn-row"><a class="btn" href="/destinations/">Explore destinations</a><a class="btn ghost" href="#newsletter">Get the weekly letter</a></div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head"><h2>This week in travel</h2><a href="/news/">All news →</a></div>
    {news_html}
  </div>
</section>

<section class="section alt">
  <div class="wrap feature">
    <div>
      <p class="eyebrow">Destination of the week</p>
      <h2>{esc(featured['title'])}, {esc(featured['country'])}</h2>
      <p class="lead">{esc(featured['tagline'])}</p>
      <p class="muted">Best time to go: {esc(featured['best_time'])}</p>
      <p><span class="score-inline">Budget luxury score {featured['score']}/10</span></p>
      <a class="btn" href="/destinations/{featured['slug']}/">Read the guide</a>
    </div>
    <a class="feature-art" href="/destinations/{featured['slug']}/" aria-label="{esc(featured['title'])} guide">{art_svg(featured['slug']+'-f', featured.get('art'), 900, 700, featured['title'])}</a>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head"><h2>Small changes. Better journeys.</h2><a href="/tips/">All tips →</a></div>
    <div class="grid three">{''.join(tip_card(t) for t in TIPS[:3])}</div>
  </div>
</section>

<section class="section alt">
  <div class="wrap">
    <div class="section-head"><h2>Destinations</h2><a href="/destinations/">See all →</a></div>
    <div class="grid three">{''.join(dest_card(d) for d in DESTS[:6])}</div>
  </div>
</section>

<section class="section">
  <div class="wrap about-teaser">
    <p class="big-number">90+</p>
    <div>
      <h2>Written by someone who has been there</h2>
      <p>Scandinavian Nomads is written by a Norwegian traveller with more than 25 years in aviation, hotels, restaurants and destination management, and more than 90 countries visited. The goal is simple: to help you travel better, not just cheaper.</p>
      <a class="more" href="/about/">About Scandinavian Nomads →</a>
    </div>
  </div>
</section>
"""
    page("/", SITE["name"], SITE["description"], body)


def build_destinations():
    filters = "".join(f'<button class="chip" data-filter="{esc(r)}">{esc(r)}</button>' for r in REGIONS)
    body = f"""
<section class="page-head"><div class="wrap">
  <p class="eyebrow">Destination guides</p>
  <h1>Where to go for luxury on a budget</h1>
  <p class="lead">Every guide has a budget luxury score: how much luxury experience you get per krone spent.</p>
</div></section>
<section class="section tight"><div class="wrap">
  <div class="chips" role="group" aria-label="Filter by region"><button class="chip active" data-filter="all">All</button>{filters}</div>
  <div class="grid three" id="dest-grid">{''.join(dest_card(d) for d in DESTS)}</div>
  <p class="empty-note" id="dest-empty" hidden>No guides for this region yet. They are on the way.</p>
</div></section>"""
    page("/destinations/", "Destination guides", "Budget-luxury destination guides: where to stay, what to eat, how to save and a 3-day itinerary.", body, "Destinations")

    for d in DESTS:
        html_body = d["html"]
        btn = inline_hotel_button(d)
        if btn:
            html_body = re.sub(r"(<h2>Where to stay</h2>\s*<p>.*?</p>)", lambda m: m.group(1) + btn, html_body, count=1, flags=re.S)
        body = f"""
<article class="guide">
  <header class="guide-hero">
    <div class="guide-art">{art_svg(d['slug']+'-h', d.get('art'), 1600, 800, d['title'])}</div>
    <div class="wrap guide-head">
      {sponsored_badge(d)}
      <p class="eyebrow light">{esc(d['country'])} · {esc(d['region'])}</p>
      <h1>{esc(d['title'])}</h1>
      <p class="lead">{esc(d['tagline'])}</p>
    </div>
  </header>
  <div class="wrap guide-layout">
    <div class="prose">{html_body}{affiliate_box(d)}</div>
    <aside class="facts">
      <div class="fact"><span>Budget luxury score</span><strong>{d['score']}/10</strong></div>
      <div class="fact"><span>Best time to visit</span><p>{esc(d['best_time'])}</p></div>
      <div class="fact"><span>Updated</span><p>{fmt_date(d['published'])}</p></div>
      <a class="btn full" href="#newsletter">Get new guides by email</a>
    </aside>
  </div>
</article>
<section class="section alt"><div class="wrap">
  <div class="section-head"><h2>More destinations</h2><a href="/destinations/">All guides →</a></div>
  <div class="grid three">{''.join(dest_card(x) for x in [x for x in DESTS if x['slug'] != d['slug']][:3])}</div>
</div></section>"""
        page(f"/destinations/{d['slug']}/", f"{d['title']} travel guide", f"{d['title']}, {d['country']}: {d['tagline']}", body, "Destinations", kind="article")


def build_tips():
    groups = ""
    for cat in TIP_CATEGORIES:
        items = [t for t in TIPS if t["category"] == cat]
        if items:
            groups += f'<h2 class="group-title">{esc(cat)}</h2><div class="grid three">{"".join(tip_card(t) for t in items)}</div>'
    body = f"""
<section class="page-head"><div class="wrap">
  <p class="eyebrow">Tips</p>
  <h1>Budget-luxury tips</h1>
  <p class="lead">Practical ways to fly, stay and eat better without paying full price.</p>
</div></section>
<section class="section tight"><div class="wrap">{groups}</div></section>"""
    page("/tips/", "Budget-luxury travel tips", "Practical tips on points, boutique hotels, fine dining, planning and gear for luxury travel on a budget.", body, "Tips")
    for t in TIPS:
        others = [x for x in TIPS if x["slug"] != t["slug"]][:3]
        body = f"""
<article class="article">
  <header class="page-head"><div class="wrap narrow">
    {sponsored_badge(t)}
    <p class="eyebrow"><a href="/tips/">Tips</a> · {esc(t['category'])}</p>
    <h1>{esc(t['title'])}</h1>
    <p class="lead">{esc(t['summary'])}</p>
    <p class="muted small">Published {fmt_date(t['published'])}</p>
  </div></header>
  <div class="wrap narrow prose">{t['html']}{products_box(t)}</div>
</article>
<section class="section alt"><div class="wrap">
  <div class="section-head"><h2>More tips</h2><a href="/tips/">All tips →</a></div>
  <div class="grid three">{''.join(tip_card(x) for x in others)}</div>
</div></section>"""
        page(f"/tips/{t['slug']}/", t["title"], t["summary"], body, "Tips", kind="article")


def build_news():
    cards = []
    for n in NEWS:
        label = "Coming soon" if n.get("placeholder") else f"Week {n['week']}, {n['year']}"
        cards.append(f"""<a class="card news-card" href="/news/{n['slug']}/">
  <div class="card-body"><p class="eyebrow">{label} · {fmt_date(n['published'])}</p><h3>{esc(n['title'])}</h3><p>{esc(n['summary'])}</p><span class="more">Read →</span></div>
</a>""")
    body = f"""
<section class="page-head"><div class="wrap">
  <p class="eyebrow">Travel news</p>
  <h1>This week in travel</h1>
  <p class="lead">A short roundup every Monday: the travel news that matters for budget-luxury travellers, with sources.</p>
</div></section>
<section class="section tight"><div class="wrap"><div class="grid two">{''.join(cards)}</div></div></section>"""
    page("/news/", "Weekly travel news", "Weekly travel news roundup for budget-luxury travellers: routes, hotels, loyalty programmes and deals.", body, "Travel News")
    for n in NEWS:
        label = "Coming soon" if n.get("placeholder") else f"Week {n['week']}, {n['year']}"
        body = f"""
<article class="article">
  <header class="page-head"><div class="wrap narrow">
    {sponsored_badge(n)}
    <p class="eyebrow"><a href="/news/">Travel news</a> · {label}</p>
    <h1>{esc(n['title'])}</h1>
    <p class="lead">{esc(n['summary'])}</p>
    <p class="muted small">Published {fmt_date(n['published'])}</p>
  </div></header>
  <div class="wrap narrow">
    <div class="prose">{n['html']}</div>
    <div class="news-list">{news_items_html(n.get('items') or [])}</div>
  </div>
</article>"""
        page(f"/news/{n['slug']}/", n["title"], n["summary"], body, "Travel News", kind="article")


def build_toolkit():
    blocks = []
    for c in SITE["toolkit"]:
        tools = c.get("tools") or []
        if tools:
            inner = "".join(f"""<div class="tool"><h3>{esc(t['name'])}</h3><p>{esc(t.get('why', ''))}</p>
<a class="btn small" href="{esc(t['url'])}" target="_blank" rel="sponsored nofollow noopener">Visit {esc(t['name'])} →</a></div>""" for t in tools)
        else:
            inner = '<p class="empty-note">Our picks are coming soon.</p>'
        blocks.append(f'<section class="toolkit-cat"><h2>{esc(c["category"])}</h2><p class="muted">{esc(c["intro"])}</p><div class="tools">{inner}</div></section>')
    any_tools = any(c.get("tools") for c in SITE["toolkit"])
    disc = f'<p class="disclosure-line">{DISCLOSURE_LINE} <a href="/disclosure/">Learn more</a>.</p>' if any_tools else ""
    body = f"""
<section class="page-head"><div class="wrap narrow">
  <p class="eyebrow">Travel toolkit</p>
  <h1>The tools we actually use</h1>
  <p class="lead">Booking sites, apps and gear that help you travel better for less. Tested, compared and updated.</p>
  {disc}
</div></section>
<section class="section tight"><div class="wrap narrow">{''.join(blocks)}</div></section>"""
    page("/toolkit/", "Travel toolkit", "The booking sites, apps and travel gear Scandinavian Nomads recommends for budget-luxury travel.", body, "Toolkit")


def build_static_pages():
    about = """
<section class="page-head"><div class="wrap narrow">
  <p class="eyebrow">About</p>
  <h1>Luxury is a way of travelling, not a price</h1>
</div></section>
<section class="section tight"><div class="wrap narrow prose">
<p>Scandinavian Nomads started with a simple observation: the best travel moments are rarely the most expensive ones. A sea-view cabin in Lofoten, a long lunch in Lisbon, the Star Ferry at dusk in Hong Kong. With the right timing and a few insider tricks, you can travel in real comfort without paying full luxury prices.</p>
<p>The site is written by a Norwegian who grew up between mountains and fjords and has since visited more than 90 countries. Over 25 years he has worked as cabin crew, purser and base manager in aviation, as a destination manager opening and running destinations in several countries, as a restaurant manager, and in hospitality at sea. That means the tips here come from both sides of the counter: as a traveller, and as someone who has run the hotels, flights and restaurants you book.</p>
<h2>The budget-luxury philosophy</h2>
<ul>
<li><strong>Spend where it matters.</strong> A great bed, a great view and one memorable meal beat ten average ones.</li>
<li><strong>Timing is everything.</strong> Shoulder season and lunch menus are the two biggest secrets in travel.</li>
<li><strong>Be honest.</strong> If something is overpriced, we say so. Sponsored content is always clearly labelled.</li>
</ul>
<h2>Weekly updates</h2>
<p>Every week we publish a travel-news roundup, a new destination guide and a new tip. <a href="#newsletter">Subscribe to the newsletter</a> to get them by email.</p>
</div></section>"""
    page("/about/", "About", "The story and philosophy behind Scandinavian Nomads, a budget-luxury travel site.", about, "About")

    contact = f"""
<section class="page-head"><div class="wrap narrow">
  <p class="eyebrow">Contact</p>
  <h1>Get in touch</h1>
  <p class="lead">Questions, tips, press or partnership enquiries. We read every message.</p>
</div></section>
<section class="section tight"><div class="wrap narrow">
  <form class="contact-form" action="/contact.php" method="post">
    <label>Name<input type="text" name="name" required maxlength="100"></label>
    <label>Email<input type="email" name="email" required maxlength="200"></label>
    <label>Subject<select name="topic"><option>General question</option><option>Partnership / collaboration</option><option>Press</option><option>Tip for a story</option></select></label>
    <label>Message<textarea name="message" rows="6" required maxlength="5000"></textarea></label>
    <input type="text" name="website" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
    <button type="submit">Send message</button>
    <p class="fineprint">Or email us directly at <a href="mailto:{SITE['email']}">{SITE['email']}</a>.</p>
  </form>
</div></section>
{newsletter_block(inline=True)}"""
    page("/contact/", "Contact", "Contact Scandinavian Nomads for questions, partnerships and press.", contact, "Contact")

    disclosure = """
<section class="page-head"><div class="wrap narrow"><p class="eyebrow">Transparency</p><h1>Affiliate disclosure</h1></div></section>
<section class="section tight"><div class="wrap narrow prose">
<p>Scandinavian Nomads is free to read. To keep it that way, we may earn money in the following ways:</p>
<h2>Affiliate links</h2>
<p>Some links on this site are affiliate links. If you click one and make a booking or purchase, we may earn a small commission from the provider. <strong>It costs you nothing extra</strong>, and sometimes you get the same or a better price than going direct.</p>
<p>Affiliate links are marked with a note next to them. We only recommend hotels, services and products we would use ourselves, and a commission never decides what we recommend or how we rate a destination.</p>
<h2>Sponsored content</h2>
<p>We may occasionally publish content created in cooperation with a hotel, tourist board or brand. Such content is always clearly labelled <strong>"Sponsored"</strong> (in Norwegian: <em>annonse</em>) at the top, in line with the Norwegian Marketing Control Act (<em>markedsføringsloven</em>) and the guidance of the Norwegian Consumer Authority (<em>Forbrukertilsynet</em>).</p>
<h2>Independence</h2>
<p>Our opinions are our own. If something is overpriced or disappointing, we will say so, sponsored or not.</p>
<p>Questions? Contact us at <a href="mailto:connect@scandinaviannomads.com">connect@scandinaviannomads.com</a>.</p>
</div></section>"""
    page("/disclosure/", "Affiliate disclosure", "How Scandinavian Nomads earns money: affiliate links and clearly labelled sponsored content.", disclosure)

    privacy = """
<section class="page-head"><div class="wrap narrow"><p class="eyebrow">Privacy</p><h1>Privacy policy</h1></div></section>
<section class="section tight"><div class="wrap narrow prose">
<p>This policy explains what personal data Scandinavian Nomads collects and how it is used.</p>
<h2>Newsletter</h2>
<p>If you subscribe, we store your email address to send you the newsletter. You can unsubscribe at any time using the link in every email or by contacting us, and we will delete your address.</p>
<h2>Contact form</h2>
<p>When you send a message, we receive your name, email address and message so we can reply. We do not use it for anything else.</p>
<h2>Affiliate links and cookies</h2>
<p>This site itself does not use advertising or tracking cookies. When you click an affiliate link, the partner's website may set cookies to register that you came from us. See the partner's own privacy policy for details.</p>
<h2>Your rights</h2>
<p>Under the GDPR you can ask to see, correct or delete the personal data we hold about you. Contact <a href="mailto:connect@scandinaviannomads.com">connect@scandinaviannomads.com</a>.</p>
</div></section>"""
    page("/privacy/", "Privacy policy", "Privacy policy for Scandinavian Nomads.", privacy)

    for slug, title, text in [("thanks", "Thank you", "Your message is on its way. We usually reply within a few days."),
                               ("subscribed", "You're in", "Thanks for subscribing to the good travel letter. Look out for the next issue on Monday."),
                               ("oops", "Something went wrong", "We could not send your form. Please try again, or email connect@scandinaviannomads.com.")]:
        body = f'<section class="page-head center"><div class="wrap narrow"><h1>{title}</h1><p class="lead">{text}</p><a class="btn" href="/">Back to the homepage</a></div></section>'
        page(f"/{slug}/", title, text, body)

    body = '<section class="page-head center"><div class="wrap narrow"><p class="eyebrow">404</p><h1>This page has wandered off</h1><p class="lead">The page you were looking for does not exist.</p><a class="btn" href="/destinations/">Explore destinations</a></div></section>'
    page("/404.html", "Page not found", "Page not found.", body)


def build_feeds(paths):
    urls = "".join(f"<url><loc>{BASE}{p}</loc></url>" for p in paths)
    (DIST / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>', encoding="utf-8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n", encoding="utf-8")
    items = ""
    for n in NEWS + DESTS + TIPS:
        kind = "news" if n in NEWS else "destinations" if n in DESTS else "tips"
        link = f"{BASE}/{kind}/{n['slug']}/"
        desc = n.get("summary") or n.get("tagline") or ""
        pub = dt.datetime.combine(n["published"], dt.time(7, 0)).strftime("%a, %d %b %Y %H:%M:%S +0000")
        items += f"<item><title>{esc(n['title'])}</title><link>{link}</link><guid>{link}</guid><pubDate>{pub}</pubDate><description>{esc(desc)}</description></item>"
    (DIST / "feed.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>{esc(SITE["name"])}</title><link>{BASE}/</link><description>{esc(SITE["description"])}</description>{items}</channel></rss>', encoding="utf-8")


def main():
    global ASSET_V
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    shutil.copytree(ROOT / "assets", DIST / "assets")
    for f in (ROOT / "php").glob("*"):
        shutil.copy(f, DIST / f.name)
    h = hashlib.md5()
    for f in sorted((ROOT / "assets").glob("*")):
        h.update(f.read_bytes())
    ASSET_V = h.hexdigest()[:8]
    # social share image as SVG->PNG fallback is optional; keep an SVG og too
    (DIST / "assets" / "og.svg").write_text(art_svg("og", next((d.get('art') for d in DESTS if d['slug']=='lofoten'), None), 1200, 630, SITE["name"]), encoding="utf-8")

    build_home(); build_destinations(); build_tips(); build_news(); build_toolkit(); build_static_pages()
    paths = ["/", "/destinations/", "/news/", "/tips/", "/toolkit/", "/about/", "/contact/", "/disclosure/", "/privacy/"]
    paths += [f"/destinations/{d['slug']}/" for d in DESTS] + [f"/tips/{t['slug']}/" for t in TIPS] + [f"/news/{n['slug']}/" for n in NEWS]
    build_feeds(paths)
    print(f"Built {len(paths)} pages into {DIST}")


if __name__ == "__main__":
    main()
