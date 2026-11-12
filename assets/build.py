"""Builds the profile SVGs, each as {wide,narrow} x {light,dark}:

- header-*: a flight path over a contour map whose waypoints are the stacks
  picked up over the years, with a drone that keeps flying the route;
- status-*, telemetry-*: head-up-display strips.

    python3 assets/build.py

Motion stops under prefers-reduced-motion.
"""
import math
from pathlib import Path

WAYPOINTS = [
    ("2023", "Java, Python"),
    ("2023", "React"),
    ("2025", "Next.js"),
    ("2025", "OpenLayers GIS"),
    ("2026", "TypeScript SaaS"),
    ("2026", "AI agents"),
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
        points=[(110, 284), (290, 236), (480, 284), (680, 226), (870, 162), (1040, 112)],
        end=(1132, 62), label="below", year=20, text=19, drone=1.0,
        hills=[(930, 250, 300, 150), (250, 330, 260, 120), (620, 40, 240, 90)],
    ),
    "narrow": dict(
        w=640, h=740, title=(44, 108, 68), sub=(46, 152, 24),
        points=[(110, 250), (250, 330), (130, 410), (270, 490), (150, 570), (290, 650)],
        end=(470, 700), label="right", year=27, text=27, drone=1.15,
        hills=[(520, 330, 230, 190), (90, 700, 200, 120), (560, 60, 180, 90)],
    ),
}

FONT = "'Avenir Next','Segoe UI','Helvetica Neue',Arial,sans-serif"

STRIPS = {
    "status": ("NOW FLYING", "AI agents, TypeScript, maps", True),
    "telemetry": ("TELEMETRY", "live from GitHub", False),
}
STRIP_SIZES = {"wide": (1200, 48, 18), "narrow": (640, 60, 23)}

MOTION = (
    "<style>.still{display:none}"
    ".pulse{transform-box:fill-box;transform-origin:center;animation:pulse 3.2s ease-out infinite}"
    ".blink{animation:blink 1.6s steps(1) infinite}"
    "@keyframes pulse{0%{transform:scale(1);opacity:.9}70%,100%{transform:scale(2.6);opacity:0}}"
    "@keyframes blink{50%{opacity:.25}}"
    "@media (prefers-reduced-motion:reduce){.fly{display:none}.still{display:inline}"
    ".pulse{animation:none;opacity:0}.blink{animation:none}}</style>"
)


def brackets(c, w, h, inset, size):
    """Four corner brackets, the frame of a head-up display."""
    a, b, x, y = inset, inset + size, w - inset, h - inset
    d = (f"M{a},{b} V{a} H{b} M{x - size},{a} H{x} V{b} "
         f"M{x},{y - size} V{y} H{x - size} M{b},{y} H{a} V{y - size}")
    return f'<path d="{d}" fill="none" stroke="{c["soft"]}" stroke-width="2" stroke-linecap="round"/>'


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
        f'aria-label="DankangE. A flight path over a contour map with six waypoints: '
        + "; ".join(f"{y} {t}" for y, t in WAYPOINTS) + '.">',
        MOTION,
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
    out.append(brackets(c, w, h, 18, 22))
    for n, ((x, y), (year, text)) in enumerate(zip(L["points"], WAYPOINTS)):
        out.append(f'<circle class="pulse" style="animation-delay:{n * 0.5:.1f}s" cx="{x}" cy="{y}" r="13" '
                   f'fill="none" stroke="{c["point"]}" stroke-width="2"/>')
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
    out.append(f'<g class="fly">{drone(c, L["drone"])}'
               f'<animateMotion dur="16s" repeatCount="indefinite" calcMode="linear" keyPoints="0;1;1" '
               f'keyTimes="0;0.86;1"><mpath href="#route"/></animateMotion>'
               f'<animate attributeName="opacity" dur="16s" repeatCount="indefinite" values="0;1;1;0" '
               f'keyTimes="0;0.04;0.95;1"/></g>')
    tx, ty, ts = L["title"]
    sx, sy, ss = L["sub"]
    out.append(f'<text x="{tx}" y="{ty}" font-family="{FONT}" font-size="{ts}" font-weight="800" '
               f'letter-spacing="-2" fill="{c["ink"]}">DankangE</text>')
    out.append(f'<text x="{sx}" y="{sy}" font-family="{FONT}" font-size="{ss}" fill="{c["soft"]}">'
               f'Web developer. TypeScript, React and maps.</text>')
    out.append("</g></svg>")
    return "\n".join(out) + "\n"


def strip(name, size, theme):
    (label, detail, live), (w, h, fs), c = STRIPS[name], STRIP_SIZES[size], THEMES[theme]
    mid, x = h / 2, 34
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
           f'aria-label="{label}: {detail}">', MOTION,
           f'<rect width="{w}" height="{h}" rx="10" fill="{c["bg"]}"/>', brackets(c, w, h, 8, 10)]
    if live:
        out.append(f'<circle class="pulse" cx="{x + 6}" cy="{mid}" r="6" fill="none" stroke="{c["point"]}" stroke-width="2"/>'
                   f'<circle class="blink" cx="{x + 6}" cy="{mid}" r="6" fill="{c["point"]}"/>')
        x += 28
    label_w = len(label) * fs * 0.74
    out.append(f'<text x="{x}" y="{mid + fs * 0.35:.1f}" font-family="{FONT}" font-size="{fs}" font-weight="700" '
               f'letter-spacing="1.5" fill="{c["ink"]}">{label}</text>'
               f'<text x="{x + label_w + 14:.0f}" y="{mid + fs * 0.35:.1f}" font-family="{FONT}" font-size="{fs}" '
               f'fill="{c["soft"]}">{detail}</text>')
    start = x + label_w + 14 + len(detail) * fs * 0.52 + 24
    ticks = "".join(f"M{t:.0f},{mid - (7 if i % 5 == 0 else 3)} V{mid + (7 if i % 5 == 0 else 3)} "
                    for i, t in enumerate(range(int(start), w - 34, 12)))
    out.append(f'<path d="{ticks}" stroke="{c["contour"]}" stroke-width="2" stroke-linecap="round"/></svg>')
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    here = Path(__file__).parent
    for theme in THEMES:
        for layout in LAYOUTS:
            (here / f"header-{layout}-{theme}.svg").write_text(build(layout, theme))
        for name in STRIPS:
            for size in STRIP_SIZES:
                (here / f"{name}-{size}-{theme}.svg").write_text(strip(name, size, theme))
