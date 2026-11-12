"""Builds the profile header SVGs: a flight path over a contour map whose
waypoints are the stacks in the public repos, in the order they were picked up.

    python3 assets/build_header.py

Writes header-{wide,narrow}-{light,dark}.svg next to this file.
"""
import math
from pathlib import Path

WAYPOINTS = [
    ("2023", "Java, Python"),
    ("2023", "React"),
    ("2025", "Next.js"),
    ("2025", "OpenLayers GIS"),
    ("2026", "TypeScript SaaS"),
]

THEMES = {
    "light": dict(bg="#EAF1F8", contour="#C3D3E3", ink="#12263A", soft="#4A6077",
                  path="#2F6FDE", point="#E8940C", halo="#EAF1F8"),
    "dark": dict(bg="#0E1B2A", contour="#1F3550", ink="#EAF1F8", soft="#9DB2C8",
                 path="#6FA0FF", point="#F2B14A", halo="#0E1B2A"),
}

LAYOUTS = {
    "wide": dict(
        w=1200, h=360, title=(64, 118, 76), sub=(66, 160, 23),
        points=[(120, 286), (340, 232), (570, 288), (810, 196), (1030, 128)],
        end=(1128, 74), label="below", year=20, text=19, drone=1.0,
        hills=[(930, 250, 300, 150), (250, 330, 260, 120), (620, 40, 240, 90)],
    ),
    "narrow": dict(
        w=640, h=660, title=(44, 108, 68), sub=(46, 152, 24),
        points=[(110, 250), (250, 330), (130, 410), (270, 490), (150, 570)],
        end=(330, 622), label="right", year=27, text=27, drone=1.15,
        hills=[(520, 330, 230, 190), (90, 620, 200, 120), (560, 60, 180, 90)],
    ),
}

FONT = "'Avenir Next','Segoe UI','Helvetica Neue',Arial,sans-serif"


def contour(cx, cy, rx, ry, scale, seed):
    pts = []
    for i in range(49):
        a = 2 * math.pi * i / 48
        wobble = 1 + 0.09 * math.sin(3 * a + seed) + 0.05 * math.sin(5 * a + 2 * seed)
        pts.append((cx + rx * scale * wobble * math.cos(a), cy + ry * scale * wobble * math.sin(a)))
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z"


def smooth(points):
    """Catmull-Rom spline through the points, as cubic Bezier segments."""
    p = [points[0]] + points + [points[-1]]
    d = f"M{points[0][0]},{points[0][1]}"
    for i in range(1, len(p) - 2):
        (x0, y0), (x1, y1), (x2, y2), (x3, y3) = p[i - 1], p[i], p[i + 1], p[i + 2]
        d += (f" C{x1 + (x2 - x0) / 6:.1f},{y1 + (y2 - y0) / 6:.1f}"
              f" {x2 - (x3 - x1) / 6:.1f},{y2 - (y3 - y1) / 6:.1f} {x2},{y2}")
    return d


def drone(c, scale):
    rotors = "".join(
        f'<circle cx="{x}" cy="{y}" r="9" fill="none" stroke="{c["ink"]}" stroke-width="2.5"/>'
        for x in (-15, 15) for y in (-15, 15))
    return (f'<g transform="scale({scale})">'
            f'<circle r="34" fill="{c["halo"]}"/>'
            f'<path d="M-15,-15 L15,15 M15,-15 L-15,15" stroke="{c["ink"]}" stroke-width="3.5" stroke-linecap="round"/>'
            f'{rotors}<rect x="-7" y="-7" width="14" height="14" rx="4" fill="{c["point"]}"/></g>')


def build(layout, theme):
    L, c = LAYOUTS[layout], THEMES[theme]
    w, h = L["w"], L["h"]
    route = smooth(L["points"] + [L["end"]])
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
        f'aria-label="DankangE. A flight path over a contour map with five waypoints: '
        + "; ".join(f"{y} {t}" for y, t in WAYPOINTS) + '.">',
        "<style>.still{display:none}@media (prefers-reduced-motion:reduce){.fly{display:none}.still{display:inline}}</style>",
        f'<clipPath id="card"><rect width="{w}" height="{h}" rx="20"/></clipPath>',
        f'<g clip-path="url(#card)"><rect width="{w}" height="{h}" fill="{c["bg"]}"/>',
        f'<g fill="none" stroke="{c["contour"]}" stroke-width="1.5">',
    ]
    for n, (cx, cy, rx, ry) in enumerate(L["hills"]):
        for ring in range(1, 6):
            out.append(f'<path d="{contour(cx, cy, rx, ry, ring / 5, n * 1.7 + ring * 0.25)}"/>')
    out.append("</g>")
    out.append(f'<path id="route" d="{route}" fill="none" stroke="{c["path"]}" stroke-width="3" '
               f'stroke-dasharray="2 11" stroke-linecap="round"/>')
    for (x, y), (year, text) in zip(L["points"], WAYPOINTS):
        out.append(f'<circle cx="{x}" cy="{y}" r="13" fill="{c["bg"]}" stroke="{c["point"]}" stroke-width="3"/>'
                   f'<circle cx="{x}" cy="{y}" r="5" fill="{c["point"]}"/>')
        if L["label"] == "below":
            out.append(f'<text x="{x}" y="{y + 42}" text-anchor="middle" font-family="{FONT}" font-size="{L["year"]}" '
                       f'font-weight="700" fill="{c["ink"]}">{year}</text>'
                       f'<text x="{x}" y="{y + 66}" text-anchor="middle" font-family="{FONT}" font-size="{L["text"]}" '
                       f'fill="{c["soft"]}">{text}</text>')
        else:
            out.append(f'<text x="{x + 34}" y="{y + 9}" font-family="{FONT}" font-size="{L["year"]}" fill="{c["soft"]}">'
                       f'<tspan font-weight="700" fill="{c["ink"]}">{year}</tspan>  {text}</text>')
    ex, ey = L["end"]
    out.append(f'<g class="still" transform="translate({ex},{ey})">{drone(c, L["drone"])}</g>')
    out.append(f'<g class="fly">{drone(c, L["drone"])}<animateMotion dur="9s" begin="0.4s" fill="freeze" '
               f'calcMode="spline" keyTimes="0;1" keySplines="0.4 0 0.2 1"><mpath href="#route"/></animateMotion></g>')
    tx, ty, ts = L["title"]
    sx, sy, ss = L["sub"]
    out.append(f'<text x="{tx}" y="{ty}" font-family="{FONT}" font-size="{ts}" font-weight="800" '
               f'letter-spacing="-2" fill="{c["ink"]}">DankangE</text>')
    out.append(f'<text x="{sx}" y="{sy}" font-family="{FONT}" font-size="{ss}" fill="{c["soft"]}">'
               f'Web developer. TypeScript, React and maps.</text>')
    out.append("</g></svg>")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    here = Path(__file__).parent
    for layout in LAYOUTS:
        for theme in THEMES:
            (here / f"header-{layout}-{theme}.svg").write_text(build(layout, theme))
