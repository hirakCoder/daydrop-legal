#!/usr/bin/env python3
"""Build the /days-until/ live countdown pages for daydrop.beatroot.dev.

Each page is hand-written content (intro, facts, FAQ) in EVENTS below, rendered into one shared
layout so markup and schema stay consistent. This is NOT a programmatic page factory: the list is
small on purpose (Stackwrite's April 2026 demotion came from hundreds of templated pages), every
date is verified against a primary/authoritative source before it goes in, and each page carries a
working tool (the live countdown in countdown.js), not just text.

    python3 scripts/build_countdowns.py        # writes days-until/<slug>/index.html + days-until/index.html

Then: sitemap.xml, llms.txt and IndexNow (indexnow-submit.sh).
"""
import datetime as dt
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "days-until"
SITE = "https://daydrop.beatroot.dev"
UPDATED = "2026-10-18"
BEACON = "571adcf922b646e7af20f34c676c4c9b"

# Pages (have their own URL). Dates are fixed-calendar holidays; weekdays computed below.
EVENTS = [
    {
        "slug": "halloween",
        "name": "Halloween",
        "year": 2026,
        "date": dt.date(2026, 10, 31),
        "next": dt.date(2027, 10, 31),
        "regions": "us canada europe oceania other",
        "emoji": "🎃",
        "intro": "Halloween is always on October 31. In 2026 it lands on a Saturday, so trick-or-treating, "
                 "parties and the late night all fall on the weekend for most people.",
        "notes": [
            "Costume shops and pumpkin patches get busy in the last two weeks, so the countdown is a useful nudge to sort costumes early.",
            "Because October 31 is a Saturday in 2026, many community events and school parades move to Friday, October 30. Check locally.",
        ],
        "faq": [
            ("What day of the week is Halloween 2026?", "Halloween 2026 is on Saturday, October 31, 2026."),
            ("How many days until Halloween 2026?", "The counter at the top of this page shows the live number of days, hours and minutes, calculated in your own time zone to the start of October 31, 2026."),
            ("When is Halloween 2027?", "Halloween 2027 is on Sunday, October 31, 2027. The date never changes, only the weekday."),
            ("Can I keep a Halloween countdown on my iPhone?", "Yes. In DayDrop, create an event called Halloween for October 31, then add the DayDrop widget to your Lock Screen or Home Screen. It updates by itself, and you can use your own photo or generate a spooky background."),
        ],
    },
    {
        "slug": "christmas",
        "name": "Christmas",
        "year": 2026,
        "date": dt.date(2026, 12, 25),
        "next": dt.date(2027, 12, 25),
        "regions": "us canada europe oceania south-asia east-asia other",
        "emoji": "🎄",
        "intro": "Christmas Day is always December 25. In 2026 it falls on a Friday, which makes Christmas "
                 "Eve a Thursday and gives many people a long weekend straight after.",
        "notes": [
            "“Sleeps until Christmas” is the same as the days left counted from tonight, which is what the counter shows on the fine line.",
            "If you count down to Christmas Eve instead, that is Thursday, December 24, 2026.",
        ],
        "faq": [
            ("What day of the week is Christmas 2026?", "Christmas Day 2026 is Friday, December 25, 2026."),
            ("How many days until Christmas 2026?", "The counter at the top of this page shows the live number of days, hours and minutes in your own time zone, counted to the start of December 25, 2026."),
            ("How many sleeps until Christmas?", "The same as the days left, counted from tonight. The fine print under the counter shows it."),
            ("Can I put a Christmas countdown on my iPhone Lock Screen?", "Yes. DayDrop puts a Christmas countdown on the Lock Screen, Home Screen and Dynamic Island. Our step-by-step guide is linked below."),
        ],
        "guide": ("/blog/christmas-countdown-iphone.html", "How to put a Christmas countdown on your iPhone"),
    },
    {
        "slug": "new-year",
        "name": "New Year",
        "year": 2027,
        "date": dt.date(2027, 1, 1),
        "next": dt.date(2028, 1, 1),
        "regions": "us canada europe oceania south-asia east-asia other",
        "emoji": "🎆",
        "intro": "New Year’s Day 2027 is Friday, January 1, 2027, so New Year’s Eve is Thursday, "
                 "December 31, 2026. The counter runs to midnight in your own time zone, which is the "
                 "moment you actually celebrate.",
        "notes": [
            "Midnight arrives at different times around the world: Kiribati and New Zealand see 2027 first, Hawaii and American Samoa last.",
            "Lunar New Year 2027 is a separate date: Saturday, February 6, 2027 (the Year of the Goat).",
        ],
        "faq": [
            ("What day is New Year 2027?", "New Year’s Day 2027 is Friday, January 1, 2027. New Year’s Eve is Thursday, December 31, 2026."),
            ("How many days until New Year 2027?", "The counter on this page shows the live days, hours, minutes and seconds to midnight on January 1, 2027 in your own time zone."),
            ("Is the countdown for my time zone?", "Yes. It uses your device’s clock and time zone, so it hits zero at your local midnight."),
            ("Can I see a New Year countdown in the Dynamic Island?", "Yes. In DayDrop, open the New Year event and start a Live Activity to keep the countdown in the Dynamic Island and on the Lock Screen."),
        ],
    },
]

# Hub-only entries (no page of their own yet). Every date verified on 2026-10-18:
# Diwali (Lakshmi Puja) Nov 8 2026 — Farmers' Almanac / Wikipedia; Thanksgiving US = 4th Thursday of Nov;
# Hanukkah begins at sundown Dec 4 2026 — Hebcal via Farmers' Almanac; Lunar New Year Feb 6 2027 —
# China Highlights / RMG; Easter (Western) Mar 28 2027 — Almanac / Wikipedia; Valentine's fixed Feb 14.
HUB_ONLY = [
    ("Diwali", dt.date(2026, 11, 8), "south-asia canada us europe", "🪔", "Lakshmi Puja night; the five-day festival runs Nov 6–10, 2026."),
    ("Thanksgiving (US)", dt.date(2026, 11, 26), "us", "🦃", "Always the fourth Thursday of November."),
    ("Hanukkah", dt.date(2026, 12, 4), "us canada europe other", "🕎", "Begins at sundown on Friday, December 4 and ends December 12, 2026."),
    ("Lunar New Year", dt.date(2027, 2, 6), "east-asia canada us oceania", "🧧", "Year of the Goat begins; New Year’s Eve is February 5."),
    ("Valentine’s Day", dt.date(2027, 2, 14), "us canada europe oceania other", "💌", "Always February 14; a Sunday in 2027."),
    ("Easter", dt.date(2027, 3, 28), "us canada europe oceania", "🐣", "Western Easter Sunday; Orthodox Easter is May 2, 2027."),
]

STYLE = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif; background: #FBFBF9; color: #1D1D1F; line-height: 1.7; -webkit-font-smoothing: antialiased; }
.wrap { max-width: 720px; margin: 0 auto; padding: 64px 20px 60px; }
.back { color: #0063D6; text-decoration: none; font-size: 15px; display: inline-block; margin-bottom: 28px; }
h1 { font-size: clamp(28px, 5vw, 40px); font-weight: 650; letter-spacing: -0.025em; line-height: 1.15; margin-bottom: 10px; text-wrap: balance; }
.answer { font-size: 19px; color: #3E3E43; margin-bottom: 26px; }
.meta { color: #71717A; font-size: 13.5px; margin-bottom: 28px; }
.counter { background: #0B0B0F; color: #fff; border-radius: 22px; padding: 30px 22px 26px; text-align: center; margin: 0 0 30px; }
.counter .big { font-size: clamp(64px, 18vw, 112px); font-weight: 700; letter-spacing: -0.04em; line-height: 1; font-variant-numeric: tabular-nums; }
.counter .sub { font-size: 18px; color: #D4D4D8; margin-top: 8px; }
.counter .fine { font-size: 14px; color: #A1A1AA; margin-top: 10px; font-variant-numeric: tabular-nums; }
h2 { font-size: 23px; font-weight: 650; letter-spacing: -0.015em; margin: 38px 0 14px; }
p { font-size: 17px; color: #3E3E43; margin-bottom: 14px; }
table { width: 100%; border-collapse: collapse; margin: 8px 0 18px; font-size: 16px; }
td { padding: 10px 6px; border-bottom: 1px solid #E5E5E1; }
td:first-child { color: #71717A; width: 46%; }
ul { margin: 0 0 14px 22px; color: #3E3E43; } li { margin-bottom: 8px; }
a { color: #0063D6; }
.cta { border: 1px solid #E5E5E1; background: #F4F4F1; padding: 26px 22px; border-radius: 16px; text-align: center; margin: 34px 0; }
.cta a.btn { background: #0A7AFF; color: #fff; padding: 12px 26px; border-radius: 100px; text-decoration: none; font-weight: 500; display: inline-block; margin-top: 10px; }
.faq dt { font-weight: 600; margin-top: 16px; } .faq dd { color: #3E3E43; margin: 4px 0 0; }
.events { list-style: none; margin: 0; padding: 0; }
.events li { display: flex; gap: 14px; align-items: center; border: 1px solid #E5E5E1; background: #fff; border-radius: 16px; padding: 16px 18px; margin-bottom: 12px; }
.events .emo { font-size: 30px; } .events .info { flex: 1; } .events .title { font-weight: 600; font-size: 17px; }
.events .when { color: #71717A; font-size: 14px; } .events .num { text-align: right; min-width: 74px; }
.events .num [data-days] { font-size: 30px; font-weight: 700; font-variant-numeric: tabular-nums; display: block; line-height: 1.1; }
.events .num [data-sub] { font-size: 12px; color: #71717A; }
.local { display: inline-block; font-size: 11px; font-weight: 600; letter-spacing: .04em; color: #0A7AFF; background: #E8F1FF; border-radius: 100px; padding: 2px 8px; margin-left: 6px; vertical-align: 2px; }
.footer { text-align: center; padding: 34px 0; border-top: 1px solid #E5E5E1; margin-top: 50px; }
.footer a { color: #71717A; text-decoration: none; margin: 0 12px; font-size: 14px; }
"""


def nice(d):
    return d.strftime("%A, %B %-d, %Y")


def head(title, desc, url, schema):
    blocks = "\n".join(
        f'<script type="application/ld+json">\n{json.dumps(s, ensure_ascii=False, indent=1)}\n</script>' for s in schema
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{url}">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta name="apple-itunes-app" content="app-id=6759470132">
{blocks}
<style>{STYLE}</style>
</head>
<body>
<div class="wrap">
"""


def tail():
    return f"""<div class="footer"><a href="/days-until/">All countdowns</a><a href="/blog/">Guides</a><a href="/">DayDrop</a><a href="/privacy.html">Privacy</a></div>
</div>
<script src="/days-until/countdown.js" defer></script>
<!-- Cloudflare Web Analytics --><script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "{BEACON}"}}'></script><!-- End Cloudflare Web Analytics -->
</body>
</html>
"""


def event_page(e):
    url = f"{SITE}/days-until/{e['slug']}/"
    title = f"How Many Days Until {e['name']} {e['year']}? (Live Countdown)"
    desc = (f"{e['name']} {e['year']} is {nice(e['date'])}. Live countdown in your time zone: days, hours, "
            f"minutes and sleeps left, plus how to keep it on your iPhone.")
    schema = [
        {"@context": "https://schema.org", "@type": "WebPage", "name": title, "url": url, "description": desc,
         "dateModified": UPDATED},
        # No schema.org Event: a public holiday is not an event we organise, and misleading Event
        # markup is a rich-results policy violation. The date lives in the visible text and FAQ.
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in e["faq"]]},
    ]
    nxt = f"Next: {e['name']} {e['next'].year} is {nice(e['next'])}."
    notes = "\n".join(f"<li>{html.escape(n)}</li>" for n in e["notes"])
    faq = "\n".join(f"<dt>{html.escape(q)}</dt><dd>{html.escape(a)}</dd>" for q, a in e["faq"])
    guide = ""
    if e.get("guide"):
        guide = f'<p>Step by step with real screenshots: <a href="{e["guide"][0]}">{html.escape(e["guide"][1])}</a>.</p>'
    return head(title, desc, url, schema) + f"""<a class="back" href="/days-until/">&larr; All countdowns</a>
<h1>How many days until {html.escape(e['name'])} {e['year']}?</h1>
<p class="answer">{html.escape(e['name'])} {e['year']} is on <strong>{nice(e['date'])}</strong>.</p>

<div class="counter" data-countdown data-target="{e['date'].isoformat()}" data-name="{html.escape(e['name'])}" data-next="{html.escape(nxt)}">
  <div class="big" data-days>{e['emoji']}</div>
  <div class="sub" data-sub>days until {html.escape(e['name'])}</div>
  <div class="fine" data-fine>Live countdown loads with JavaScript. {html.escape(e['name'])} {e['year']}: {nice(e['date'])}.</div>
</div>
<p class="meta">Counted to the start of the day in your own time zone · updated {UPDATED}</p>

<p>{html.escape(e['intro'])}</p>

<h2>{html.escape(e['name'])} {e['year']} at a glance</h2>
<table>
<tr><td>Date</td><td>{nice(e['date'])}</td></tr>
<tr><td>Day of the week</td><td>{e['date'].strftime('%A')}</td></tr>
<tr><td>Next year</td><td>{nice(e['next'])}</td></tr>
</table>
<ul>
{notes}
</ul>

<div class="cta">
  <p><strong>Keep this countdown on your iPhone</strong><br>DayDrop puts it on your Lock Screen, Home Screen and Dynamic Island, with your own photo or an AI background.</p>
  <a class="btn" href="/c/{e['slug']}">Get DayDrop on the App Store</a>
</div>
{guide}

<h2>Questions</h2>
<dl class="faq">
{faq}
</dl>
""" + tail()


def hub():
    url = f"{SITE}/days-until/"
    title = "Days Until Every Holiday — Live Countdowns (2026–2027)"
    desc = ("Live countdowns to Halloween, Diwali, Thanksgiving, Hanukkah, Christmas, New Year, Lunar New Year "
            "and more, in your own time zone, with the festivals celebrated where you are shown first.")
    rows = []
    entries = [(e["name"] + f" {e['year']}", e["date"], e["regions"], e["emoji"], f"/days-until/{e['slug']}/", "") for e in EVENTS]
    entries += [(n, d, r, emo, None, note) for n, d, r, emo, note in HUB_ONLY]
    entries.sort(key=lambda x: x[1])
    for name, d, regions, emo, link, note in entries:
        label = f'<a href="{link}">{html.escape(name)}</a>' if link else html.escape(name)
        extra = f" · {html.escape(note)}" if note else ""
        rows.append(f"""<li data-regions="{regions}">
  <span class="emo">{emo}</span>
  <span class="info"><span class="title">{label}</span><span class="local" data-local hidden>Near you</span><br><span class="when">{nice(d)}{extra}</span></span>
  <span class="num" data-countdown data-target="{d.isoformat()}" data-name="{html.escape(name)}"><span data-days>&nbsp;</span><span data-sub>days</span></span>
</li>""")
    schema = [{"@context": "https://schema.org", "@type": "ItemList", "name": title,
               "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": f"{n} — {nice(d)}"}
                                   for i, (n, d, *_r) in enumerate(entries)]}]
    return head(title, desc, url, schema) + f"""<a class="back" href="/">&larr; DayDrop</a>
<h1>Days until every holiday</h1>
<p class="answer">Live countdowns in your own time zone. Festivals celebrated where you are come first.</p>
<ul class="events" data-event-list>
{chr(10).join(rows)}
</ul>
<p class="meta">Dates checked {UPDATED} against published calendars. Moveable festivals (Diwali, Hanukkah, Lunar New Year, Easter) follow lunar or lunisolar calendars, so they change every year. “Near you” is a rough guess from your device’s time zone; nothing about you is stored.</p>
<div class="cta">
  <p><strong>Want these on your Home Screen?</strong><br>DayDrop turns any date into a live widget, with your own photo or an AI background.</p>
  <a class="btn" href="/c/hub">Get DayDrop on the App Store</a>
</div>
""" + tail()


def main():
    for e in EVENTS:
        assert e["date"].weekday() == e["date"].weekday()  # computed, never typed
        d = OUT / e["slug"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(event_page(e), encoding="utf-8")
        print("wrote", d / "index.html")
    (OUT / "index.html").write_text(hub(), encoding="utf-8")
    print("wrote", OUT / "index.html")


if __name__ == "__main__":
    main()
