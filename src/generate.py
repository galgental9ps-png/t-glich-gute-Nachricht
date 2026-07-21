from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import feedparser
from dateutil import parser as dateparser

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CONFIG = json.loads((ROOT / "sources.json").read_text(encoding="utf-8"))

@dataclass(frozen=True)
class Item:
    title: str
    summary: str
    link: str
    source: str
    category: str
    published: datetime
    score: int

def clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", html.unescape(text)).strip()

def valid_url(url: str, expected_domain: str) -> bool:
    try:
        host = (urlparse(url).hostname or "").lower()
        return host == expected_domain or host.endswith("." + expected_domain)
    except ValueError:
        return False

def parse_date(entry) -> datetime:
    for key in ("published", "updated", "created"):
        value = entry.get(key)
        if value:
            try:
                dt = dateparser.parse(value)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.astimezone(timezone.utc)
            except Exception:
                pass
    return datetime.now(timezone.utc)

def rank(title: str, summary: str) -> int:
    text = f"{title} {summary}".lower()
    pos = sum(3 for word in CONFIG["positive_keywords"] if word in text)
    neg = sum(5 for word in CONFIG["negative_keywords"] if word in text)
    return pos - neg

def fetch_items() -> list[Item]:
    items: list[Item] = []
    seen: set[str] = set()

    for source in CONFIG["sources"]:
        parsed = feedparser.parse(
            source["feed"],
            request_headers={"User-Agent": "GoodNewsMonitor/1.0 (+GitHub Pages)"}
        )
        for entry in parsed.entries[:40]:
            link = str(entry.get("link", "")).strip()
            if not link or link in seen or not valid_url(link, source["domain"]):
                continue

            title = clean(entry.get("title", ""))
            summary = clean(entry.get("summary", entry.get("description", "")))
            score = rank(title, summary)

            # Conservative publication rule: at least one positive signal and
            # no strongly negative overall score.
            if score < 2 or not title:
                continue

            seen.add(link)
            items.append(Item(
                title=title[:180],
                summary=summary[:430],
                link=link,
                source=source["name"],
                category=source["category"],
                published=parse_date(entry),
                score=score
            ))

    return sorted(items, key=lambda x: (x.score, x.published), reverse=True)[:CONFIG["max_items"]]

def fallback_items() -> list[Item]:
    """Keeps the page usable if all external feeds are temporarily unavailable."""
    now = datetime.now(timezone.utc)
    return [
        Item(
            "Heute werden neue gute Nachrichten gesammelt",
            "Die offiziellen Feeds waren vorübergehend nicht erreichbar. Der Monitor versucht es beim nächsten automatischen Lauf erneut.",
            "https://www.who.int/news-room",
            "Systemhinweis",
            "Monitor",
            now,
            2
        )
    ]

def category_icon(category: str) -> str:
    return {
        "Gesundheit": "🩺", "Welt": "🌍", "Kinder": "💛",
        "Umwelt": "🌿", "Wissenschaft": "🔬", "Monitor": "📰"
    }.get(category, "✨")

def render(items: list[Item]) -> str:
    now = datetime.now().astimezone()
    date_text = now.strftime("%d.%m.%Y")

    cards = []
    for item in items:
        title = html.escape(item.title)
        summary = html.escape(item.summary or "Weitere Einzelheiten stehen in der verlinkten Originalquelle.")
        source = html.escape(item.source)
        category = html.escape(item.category)
        link = html.escape(item.link, quote=True)
        icon = category_icon(item.category)
        cards.append(f"""
        <article class="card">
          <span class="tag">{icon} {category}</span>
          <h2>{title}</h2>
          <p>{summary}</p>
          <div class="source">Quelle: <a href="{link}" target="_blank" rel="noopener noreferrer">{source}</a></div>
        </article>""")

    cards_html = "\n".join(cards)
    return f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Automatisch erzeugter Good News Monitor aus offiziellen Quellen">
<title>Daily Good News Monitor – {date_text}</title>
<style>
:root{{--paper:#fff;--ink:#102a43;--muted:#526b82;--line:#dce7f0;--blue:#176bd6;--green:#0b9a6d}}
*{{box-sizing:border-box}}
body{{margin:0;background:linear-gradient(180deg,#dff2ff 0,#f7fbff 430px,#f4f8fb 100%);font-family:Inter,system-ui,-apple-system,"Segoe UI",Arial,sans-serif;color:var(--ink)}}
a{{color:var(--blue);font-weight:800}}
.wrap{{width:min(1180px,calc(100% - 28px));margin:auto}}
.hero{{margin-top:18px;background:#fff;border-radius:28px;overflow:hidden;box-shadow:0 18px 48px rgba(18,46,74,.14)}}
.hero img{{width:100%;display:block;aspect-ratio:16/7;object-fit:cover;object-position:top}}
.hero-copy{{padding:25px 28px 29px}}
.kicker{{display:inline-block;padding:7px 11px;border-radius:999px;background:#fff0b7;color:#885600;font-weight:900;font-size:.78rem;letter-spacing:.08em;text-transform:uppercase}}
h1{{font-size:clamp(2.2rem,5vw,4.4rem);line-height:1;margin:12px 0 10px}}
.lead{{font-size:1.1rem;line-height:1.65;color:var(--muted);margin:0;max-width:920px}}
.joy{{margin:18px 0;padding:22px;text-align:center;border:2px solid #ffe085;border-radius:22px;background:linear-gradient(135deg,#fff4bd,#fff)}}
.joy strong{{display:block;font-size:clamp(1.35rem,3vw,2.1rem);margin-bottom:8px}}
.grid{{display:grid;grid-template-columns:repeat(12,1fr);gap:18px}}
.card{{grid-column:span 6;background:var(--paper);border:1px solid var(--line);border-radius:20px;padding:22px;box-shadow:0 8px 23px rgba(18,46,74,.07)}}
.card h2{{font-size:1.28rem;line-height:1.3;margin:9px 0 10px}}
.card p{{line-height:1.63;color:#38546d;margin:0}}
.tag{{display:inline-block;padding:6px 10px;border-radius:999px;background:#e8f4ff;color:#155eaa;font-size:.77rem;font-weight:900}}
.source{{margin-top:14px;padding-top:12px;border-top:1px solid var(--line);font-size:.87rem;color:var(--muted)}}
.wide{{grid-column:span 12}}
.story{{background:linear-gradient(135deg,#fff2bd,#fff)}}
.deed{{background:linear-gradient(135deg,#e6fff3,#fff)}}
footer{{text-align:center;color:var(--muted);padding:30px 0 34px}}
@media(max-width:760px){{.card,.wide{{grid-column:span 12}}}}
</style>
</head>
<body>
<div class="wrap">
<header class="hero">
<img src="../assets/goat-header.png" alt="Lustige Ziege mit pinker Sonnenbrille und Blumenkranz">
<div class="hero-copy">
<span class="kicker">Daily Good News Monitor</span>
<h1>Gute Nachrichten für {date_text}</h1>
<p class="lead">Automatisch ausgewählte positive Meldungen aus einer transparenten Liste offizieller Quellen.</p>
</div>
</header>

<section class="joy">
<strong>„Heute werden Sorgen nur in homöopathischen Dosen serviert.“ 😄</strong>
<span>Und falls doch eine zu groß gerät: Die Ziege kümmert sich darum.</span>
</section>

<main class="grid">
{cards_html}

<article class="card wide story">
<span class="tag">🌟 Positive Geschichte des Tages</span>
<h2>Fortschritt entsteht oft in vielen kleinen Schritten</h2>
<p>Hinter jeder guten Meldung stehen Menschen, die forschen, helfen, organisieren, schützen oder Wissen teilen. Der Monitor macht diese Fortschritte sichtbar.</p>
</article>

<article class="card">
<span class="tag">😄 Schmunzel-Ecke</span>
<h2>Die Ziege leitet heute die Sorgenabteilung.</h2>
<p>Sie hat alle Sorgen als „zu trocken“ eingestuft und vorsorglich die Blumen gegessen.</p>
</article>

<article class="card deed">
<span class="tag">💚 Kleine gute Tat</span>
<h2>Mach heute jemandem ein ehrliches Kompliment.</h2>
<p>Ein kurzer Satz kann länger wirken, als man denkt.</p>
</article>
</main>

<footer>Automatisch erstellt am {html.escape(now.strftime("%d.%m.%Y um %H:%M Uhr"))}. Inhalte bitte immer in der verlinkten Originalquelle prüfen.</footer>
</div>
</body>
</html>"""

def main() -> None:
    DOCS.mkdir(exist_ok=True)
    items = fetch_items() or fallback_items()
    output = render(items)
    (DOCS / "index.html").write_text(output, encoding="utf-8")
    print(f"Generated docs/index.html with {len(items)} news items.")

if __name__ == "__main__":
    main()
