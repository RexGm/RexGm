#!/usr/bin/env python3
"""Builds streak-light.svg and streak-dark.svg from GitHub's contribution calendar.

Why self-hosted instead of a streak-card service: GitHub proxies external images
through camo, which gives up after roughly four seconds. The public streak
services regularly take longer than that to answer, so the card renders as a
broken image on the profile. Committing the SVG to the repo removes the round
trip entirely -- and lets the strip use the same palette as the hero.

    python3 assets/build_streak.py [username]

Refreshed daily by .github/workflows/streak.yml.
"""

import html
import re
import sys
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from theme import MARGIN_L, MARGIN_R, MONO, SANS, THEMES  # noqa: E402

USER = sys.argv[1] if len(sys.argv) > 1 else "RexGm"
W, H = 1000, 172

CELL_RE = re.compile(r"<td\b[^>]*class=\"[^\"]*ContributionCalendar-day[^\"]*\"[^>]*>")
TIP_RE = re.compile(r"<tool-tip\b[^>]*for=\"([^\"]+)\"[^>]*>(.*?)</tool-tip>", re.S)
ATTR_RE = re.compile(r"(\w[\w-]*)=\"([^\"]*)\"")
COUNT_RE = re.compile(r"^([\d,]+)\s+contribution")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": f"{USER}-profile-builder"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def contributions(user, start, end):
    """day -> contribution count, read off the public contributions calendar.

    The calendar reflects whatever the profile itself shows, so private
    contributions are included exactly when the account opts into showing them.
    """
    counts = {}
    for year in range(start.year, end.year + 1):
        lo = max(start, date(year, 1, 1))
        hi = min(end, date(year, 12, 31))
        if lo > hi:
            continue
        page = fetch(
            f"https://github.com/users/{user}/contributions?from={lo}&to={hi}"
        )

        by_id = {}
        for tag in CELL_RE.findall(page):
            attrs = dict(ATTR_RE.findall(tag))
            if "id" in attrs and "data-date" in attrs:
                by_id[attrs["id"]] = attrs["data-date"]

        # The cell carries the date; the count only exists in its tool-tip text
        # ("3 contributions on August 3rd." / "No contributions on ...").
        for cell_id, text in TIP_RE.findall(page):
            iso = by_id.get(cell_id)
            if not iso:
                continue
            day = date.fromisoformat(iso)
            if not (lo <= day <= hi):
                continue
            m = COUNT_RE.match(html.unescape(text).strip())
            counts[day] = int(m.group(1).replace(",", "")) if m else 0
    return counts


def streaks(counts, today):
    """(total, current run, longest run) with each run's date range."""
    days = sorted(counts)
    total = sum(counts.values())

    runs, run = [], []
    for day in days:
        if counts[day] > 0:
            if run and day - run[-1] != timedelta(days=1):
                runs.append(run)
                run = []
            run.append(day)
        elif run:
            runs.append(run)
            run = []
    if run:
        runs.append(run)

    longest = max(runs, key=len) if runs else []

    # A quiet today does not break the streak -- the day is not over yet.
    current = []
    if runs:
        last = runs[-1]
        if last[-1] in (today, today - timedelta(days=1)):
            current = last

    return total, current, longest


def fmt(day):
    return f"{day.strftime('%b')} {day.day}, {day.year}"


def span(run):
    if not run:
        return "no active streak"
    if run[0] == run[-1]:
        return fmt(run[0])
    return f"{fmt(run[0])} — {fmt(run[-1])}"


def build(theme, stats, start, today):
    c = THEMES[theme]
    total, current, longest = stats
    o = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" aria-label="'
        f"{total} contributions since {fmt(start)}. Current streak "
        f"{len(current)} days. Longest streak {len(longest)} days.\">",
        f'<rect width="{W}" height="{H}" fill="{c["bg"]}"/>',
        f'<path d="M{MARGIN_L},16 H{MARGIN_R}" stroke="{c["line"]}" stroke-width="1"/>',
    ]

    cols = [
        ("TOTAL CONTRIBUTIONS", f"{total:,}", f"{fmt(start)} — present", c["text"]),
        ("CURRENT STREAK", str(len(current)), span(current), c["accent"]),
        ("LONGEST STREAK", str(len(longest)), span(longest), c["text"]),
    ]
    inner = MARGIN_R - MARGIN_L
    for i, (label, value, sub, colour) in enumerate(cols):
        cx = MARGIN_L + inner * (2 * i + 1) / 6
        o.append(
            f'<text x="{cx}" y="82" text-anchor="middle" font-family="{SANS}" '
            f'font-size="44" font-weight="640" fill="{colour}">{value}</text>'
        )
        o.append(
            f'<text x="{cx}" y="108" text-anchor="middle" font-family="{MONO}" '
            f'font-size="11" letter-spacing="2.2" fill="{c["muted"]}">{label}</text>'
        )
        o.append(
            f'<text x="{cx}" y="128" text-anchor="middle" font-family="{MONO}" '
            f'font-size="10.5" fill="{c["faint"]}">{sub}</text>'
        )

    # The current-streak column is the one that moves; underline it in accent.
    mid = MARGIN_L + inner / 2
    o.append(
        f'<path d="M{mid - 46},94 H{mid + 46}" stroke="{c["accent"]}" '
        f'stroke-width="1.4" opacity="0.55"/>'
    )
    for i in (1, 2):
        x = MARGIN_L + inner * i / 3
        o.append(f'<path d="M{x},38 V126" stroke="{c["line"]}" stroke-width="1"/>')

    o.append(f'<path d="M{MARGIN_L},146 H{MARGIN_R}" stroke="{c["line"]}" stroke-width="1"/>')
    o.append(
        f'<text x="{MARGIN_R}" y="164" text-anchor="end" font-family="{MONO}" '
        f'font-size="10" letter-spacing="0.8" fill="{c["faint"]}">'
        f'generated {today} · github.com/{USER}</text>'
    )
    o.append("</svg>")
    return "\n".join(o) + "\n"


if __name__ == "__main__":
    today = datetime.now(timezone.utc).date()
    created = fetch(f"https://api.github.com/users/{USER}")
    start = date.fromisoformat(
        re.search(r'"created_at":\s*"(\d{4}-\d{2}-\d{2})', created).group(1)
    )

    counts = contributions(USER, start, today)
    if not counts:
        raise SystemExit("no contribution data parsed -- calendar markup may have changed")

    stats = streaks(counts, today)
    print(
        f"{USER}: {stats[0]:,} contributions since {start}, "
        f"current {len(stats[1])}d, longest {len(stats[2])}d "
        f"({len(counts)} days parsed)"
    )

    out = Path(__file__).parent
    for theme in THEMES:
        path = out / f"streak-{theme}.svg"
        path.write_text(build(theme, stats, start, today), encoding="utf-8")
        print(f"wrote {path.name}")
