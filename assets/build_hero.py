#!/usr/bin/env python3
"""Builds hero-light.svg and hero-dark.svg from one geometry definition.

The hero draws the actual topology of the CodeSpells platform: a gateway in
front, three services that each own their database, an async broker, and a
side-effect consumer. Geometry lives here once so the two themes can never
drift apart -- only the palette differs.

    python3 assets/build_hero.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from theme import MONO, SANS, THEMES  # noqa: E402

W, H = 1000, 428

# --- geometry ----------------------------------------------------------------
CY = 264  # spine of the diagram

GATEWAY = (140, 238, 124, 52)  # x, y, w, h
REDIS = (150, 178, 104, 32)
SERVICES = [
    ("auth", 8081, 340, 181, 136, 46),
    ("role", 8082, 340, 241, 136, 46),
    ("booking", 8083, 340, 301, 136, 46),
]
BROKER = (576, 238, 148, 52)
MAIL = (800, 241, 124, 46)

# Orthogonal wires. Routed through two vertical channels (x=302, x=520) so the
# fan-out and fan-in read as buses instead of a tangle of diagonals.
WIRES = [
    ("M264,264 H296 Q302,264 302,258 V210 Q302,204 308,204 H340", 0.6),   # gw -> auth
    ("M264,264 H340", 0.0),                                               # gw -> role
    ("M264,264 H296 Q302,264 302,270 V318 Q302,324 308,324 H340", 1.2),   # gw -> booking
    ("M476,204 H514 Q520,204 520,210 V258 Q520,264 526,264 H576", 2.8),   # auth -> mq
    ("M476,264 H576", 2.2),                                               # role -> mq
    ("M476,324 H514 Q520,324 520,318 V270 Q520,264 526,264 H576", 3.4),   # booking -> mq
    ("M724,264 H800", 4.2),                                               # mq -> mail
]
PKT_DUR = 2.4


def db_glyph(x, cy, c):
    """A 16x15 database cylinder -- one per service, i.e. db-per-service.

    Drawn as body + two rims rather than a closed path: without the second rim
    the shape reads as a plain rounded rectangle at this size.
    """
    top = cy - 7.5
    return (
        f'<path d="M{x},{top} v15 a8,3.2 0 0 0 16,0 v-15" fill="none" '
        f'stroke="{c}" stroke-width="1.2" stroke-linecap="round"/>'
        f'<ellipse cx="{x + 8}" cy="{top}" rx="8" ry="3.2" fill="none" '
        f'stroke="{c}" stroke-width="1.2"/>'
        f'<path d="M{x},{top + 5} a8,3.2 0 0 0 16,0" fill="none" '
        f'stroke="{c}" stroke-width="1" opacity="0.55"/>'
    )


def port(x, y, text, c):
    """Real service ports, set small -- the detail that says 'this ships'."""
    return (
        f'<text x="{x}" y="{y}" text-anchor="middle" font-family="{MONO}" '
        f'font-size="9.5" letter-spacing="0.6" fill="{c}">:{text}</text>'
    )


def build(theme):
    c = THEMES[theme]
    o = []
    add = o.append

    add(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" '
        f'aria-label="Serkan Altundag, backend engineer. Architecture diagram: '
        f'api gateway fronting auth, role and booking services, each with its own '
        f'database, publishing events through RabbitMQ to a mail service.">'
    )

    # Packets are decorative; hide them outright when motion is unwelcome.
    add(
        "<style>"
        "@media (prefers-reduced-motion: reduce){.pkt{display:none}}"
        "</style>"
    )
    add(
        f'<defs><marker id="ah" viewBox="0 0 8 8" refX="7" refY="4" '
        f'markerWidth="6.5" markerHeight="6.5" orient="auto">'
        f'<path d="M0.5,0.8 L7,4 L0.5,7.2 z" fill="{c["faint"]}"/></marker></defs>'
    )
    add(f'<rect width="{W}" height="{H}" fill="{c["bg"]}"/>')

    # --- masthead ---
    add(
        f'<text x="56" y="70" font-family="{SANS}" font-size="42" font-weight="640" '
        f'letter-spacing="6.5" fill="{c["text"]}">SERKAN ALTUNDAĞ</text>'
    )
    add(
        f'<text x="58" y="99" font-family="{MONO}" font-size="13" letter-spacing="2.4" '
        f'fill="{c["muted"]}">BACKEND ENGINEER · DISTRIBUTED SYSTEMS</text>'
    )
    add(f'<path d="M56,124 H944" stroke="{c["line"]}" stroke-width="1"/>')

    # --- wires (drawn first so boxes sit on top of the line ends) ---
    for d, _ in WIRES:
        add(
            f'<path d="{d}" fill="none" stroke="{c["wire"]}" stroke-width="1.2" '
            f'marker-end="url(#ah)"/>'
        )

    # client entry
    add(
        f'<text x="56" y="268" font-family="{MONO}" font-size="12" '
        f'fill="{c["faint"]}">client</text>'
    )
    add(
        f'<path d="M104,264 H140" fill="none" stroke="{c["wire"]}" '
        f'stroke-width="1.2" stroke-dasharray="3 3" marker-end="url(#ah)"/>'
    )

    # redis, hung off the gateway
    add(
        f'<path d="M202,238 V210" fill="none" stroke="{c["wire"]}" '
        f'stroke-width="1.1" stroke-dasharray="3 3"/>'
    )
    rx, ry, rw, rh = REDIS
    add(
        f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" rx="16" '
        f'fill="{c["box"]}" stroke="{c["line"]}" stroke-width="1"/>'
    )
    add(
        f'<text x="{rx + rw / 2}" y="{ry + 21}" text-anchor="middle" '
        f'font-family="{MONO}" font-size="11.5" fill="{c["muted"]}">redis · limits</text>'
    )

    # gateway
    gx, gy, gw, gh = GATEWAY
    add(
        f'<rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" rx="4" '
        f'fill="{c["box"]}" stroke="{c["line"]}" stroke-width="1.4"/>'
    )
    add(
        f'<text x="{gx + gw / 2}" y="{CY + 4.5}" text-anchor="middle" '
        f'font-family="{MONO}" font-size="13" fill="{c["text"]}">api-gateway</text>'
    )
    add(port(gx + gw / 2, gy + gh + 14, 8080, c["faint"]))

    # services, each carrying its own database
    for name, p, sx, sy, sw, sh in SERVICES:
        scy = sy + sh / 2
        add(
            f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="4" '
            f'fill="{c["box"]}" stroke="{c["line"]}" stroke-width="1.4"/>'
        )
        add(db_glyph(sx + 14, scy, c["muted"]))
        add(
            f'<text x="{sx + 44}" y="{scy + 4.5}" font-family="{MONO}" '
            f'font-size="13" fill="{c["text"]}">{name}</text>'
        )
        add(port(sx + sw / 2, sy + sh + 14, p, c["faint"]))

    # broker -- the one accented node; everything async passes through it
    bx, by, bw, bh = BROKER
    add(
        f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="4" '
        f'fill="{c["accent_soft"]}" stroke="{c["accent"]}" stroke-width="1.4"/>'
    )
    add(
        f'<text x="{bx + bw / 2}" y="{CY - 2}" text-anchor="middle" '
        f'font-family="{MONO}" font-size="13" fill="{c["accent"]}">rabbitmq</text>'
    )
    add(
        f'<text x="{bx + bw / 2}" y="{CY + 14}" text-anchor="middle" '
        f'font-family="{MONO}" font-size="10" letter-spacing="1.2" '
        f'fill="{c["accent"]}" opacity="0.75">DOMAIN EVENTS</text>'
    )
    add(port(bx + bw / 2, by + bh + 14, 5672, c["faint"]))

    # mail
    mx, my, mw, mh = MAIL
    add(
        f'<rect x="{mx}" y="{my}" width="{mw}" height="{mh}" rx="4" '
        f'fill="{c["box"]}" stroke="{c["line"]}" stroke-width="1.4"/>'
    )
    add(db_glyph(mx + 14, CY, c["muted"]))
    add(
        f'<text x="{mx + 44}" y="{CY + 4.5}" font-family="{MONO}" font-size="13" '
        f'fill="{c["text"]}">mail</text>'
    )
    add(port(mx + mw / 2, my + mh + 14, 8084, c["faint"]))

    # --- packets ---
    for d, begin in WIRES:
        add(
            f'<circle class="pkt" r="2.6" fill="{c["accent"]}" opacity="0">'
            f'<animateMotion path="{d}" dur="{PKT_DUR}s" begin="{begin}s" '
            f'repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;1;1;0" '
            f'keyTimes="0;0.12;0.85;1" dur="{PKT_DUR}s" begin="{begin}s" '
            f'repeatCount="indefinite"/></circle>'
        )

    # --- footer ---
    add(f'<path d="M56,381 H944" stroke="{c["line"]}" stroke-width="1"/>')
    add(
        f'<text x="56" y="404" font-family="{MONO}" font-size="11.5" '
        f'fill="{c["muted"]}">java 21 · spring boot 3.5 · postgresql 16 '
        f'· rabbitmq · redis · docker</text>'
    )
    add(
        f'<text x="944" y="404" text-anchor="end" font-family="{MONO}" '
        f'font-size="11.5" letter-spacing="1" fill="{c["faint"]}">'
        f'CODESPELLS PLATFORM SERVICES</text>'
    )

    add("</svg>")
    return "\n".join(o) + "\n"


if __name__ == "__main__":
    out = Path(__file__).parent
    for theme in THEMES:
        path = out / f"hero-{theme}.svg"
        path.write_text(build(theme), encoding="utf-8")
        print(f"wrote {path.name} ({path.stat().st_size} bytes)")
