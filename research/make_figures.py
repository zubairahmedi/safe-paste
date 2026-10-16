"""Builds the study's figures as HTML (inline SVG dumbbell chart, stat tiles, results table).

    python research/make_figures.py <out_dir>
      -> <out_dir>/chart.html, tiles.html, table.html

Dumbbell: one hue, two shades (before = lighter teal, after = brand teal), validated with the
dataviz palette checker on the site's light (#F5F6F3) and dark (#111A1D) surfaces.
Hover tooltips via SVG <title>; the table is the accessible view of the same numbers.
"""
import html
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE
v0 = json.loads((HERE / "results_v1.0.json").read_text(encoding="utf-8"))
v1 = json.loads((HERE / "results_v1.1.json").read_text(encoding="utf-8"))
A0, A1, B1 = v0["A_default"], v1["A_default"], v1["B_name_in_always_hide"]

LABEL = {
    "Full names": "Full names",
    "First names after the full name": "First name used alone (after the full name)",
    "Names after a title (Ms., Dr.)": "Names after a title (Ms., Dr.)",
    "Names after family words": "Names after son, daughter, husband...",
    "Single names (mid sentence)": "Single names mid sentence",
    "ALL CAPS names": "ALL CAPS names",
    "Names in non-Latin script": "Names in Arabic, Farsi, Ge'ez script",
    "Lowercase names": "lowercase names (texting style)",
    "Single names starting a sentence": "Single names starting a sentence",
    "Word names starting a sentence (Grace, Hope)": "Grace, Hope... starting a sentence",
    "Descriptions that identify someone": "Descriptions that identify someone",
    "Phone numbers": "Phone numbers",
    "Emails": "Emails",
    "ID and health numbers": "SIN, health card, NHS, NI, SSN, IDs",
    "Dates of birth": "Dates of birth",
    "Street addresses": "Street addresses",
    "Postcodes": "Postcodes and ZIP codes",
}

groups = sorted(A1["by_group"], key=lambda g: (A1["by_group"][g]["rate"], A0["by_group"][g]["rate"]))

# ---- dumbbell chart ----
W, LW, X0, X1, ROW, TOP = 720, 290, 300, 650, 30, 64
H = TOP + ROW * len(groups) + 34
x = lambda pct: X0 + (X1 - X0) * pct / 100
parts = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-labelledby="dbt dbd" class="viz">',
         '<title id="dbt">Share of personal details Safe Paste hid, by type, version 1.0 vs 1.1</title>',
         '<desc id="dbd">Dumbbell chart for 200 made up case notes. Each row shows the share caught by version 1.0 (lighter dot) and version 1.1 (darker dot). The table below has the same numbers.</desc>']
# legend (two series -> legend always present; rows are also directly labeled)
parts.append(f'<g font-size="13"><circle cx="{X0}" cy="18" r="5" class="b"/><text x="{X0 + 12}" y="22" class="t2">Version 1.0 (before)</text>'
             f'<circle cx="{X0 + 175}" cy="18" r="6" class="a"/><text x="{X0 + 188}" y="22" class="t2">Version 1.1 (after fixes)</text></g>')
# grid + axis
for p in (0, 25, 50, 75, 100):
    parts.append(f'<line x1="{x(p):.1f}" y1="{TOP - 12}" x2="{x(p):.1f}" y2="{TOP + ROW * len(groups) - 10}" class="grid"/>'
                 f'<text x="{x(p):.1f}" y="{TOP + ROW * len(groups) + 10}" text-anchor="middle" font-size="12" class="t3">{p}%</text>')
for i, g in enumerate(groups):
    y = TOP + i * ROW
    b, a, n = A0["by_group"][g]["rate"], A1["by_group"][g]["rate"], A1["by_group"][g]["total"]
    tip = f'{LABEL[g]}: {b:g}% before, {a:g}% after ({n} tested)'
    parts.append(f'<g><title>{html.escape(tip)}</title><rect x="0" y="{y - 14}" width="{W}" height="{ROW}" fill="transparent"/>'
                 f'<text x="{LW}" y="{y + 4}" text-anchor="end" font-size="13.5" class="t1">{html.escape(LABEL[g])}</text>')
    if abs(a - b) >= 0.5:
        parts.append(f'<line x1="{x(b):.1f}" y1="{y}" x2="{x(a):.1f}" y2="{y}" class="conn"/>'
                     f'<circle cx="{x(b):.1f}" cy="{y}" r="5" class="b"/>')
    parts.append(f'<circle cx="{x(a):.1f}" cy="{y}" r="6" class="a"/>'
                 f'<text x="{X1 + 14}" y="{y + 4}" font-size="13" class="t1 v">{a:g}%</text></g>')
parts.append('</svg>')
style = """<style>
.viz{--c-before:#6AA69B;--c-after:#1D7266;overflow:visible}
@media (prefers-color-scheme: dark){:root:where(:not([data-theme="light"])) .viz{--c-before:#2F6A62;--c-after:#62C2B3}}
:root[data-theme="dark"] .viz{--c-before:#2F6A62;--c-after:#62C2B3}
.viz .a{fill:var(--c-after);stroke:var(--bg);stroke-width:2}
.viz .b{fill:var(--c-before);stroke:var(--bg);stroke-width:2}
.viz .conn{stroke:var(--c-before);stroke-width:2}
.viz .grid{stroke:var(--rule);stroke-width:1}
.viz .t1{fill:var(--ink)} .viz .t2{fill:var(--body)} .viz .t3{fill:var(--muted)} .viz .v{font-weight:700}
.viz g:hover .t1{text-decoration:underline}
.dumbbell .scroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
.dumbbell .scroll svg{min-width:640px;display:block}
.dumbbell .swipe{display:none}
@media (max-width:640px){.dumbbell .swipe{display:inline}}
.tiles{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:0 0 26px}
@media (max-width:720px){.tiles{grid-template-columns:repeat(2,minmax(0,1fr))}}
.tile{border:1px solid var(--rule);border-radius:14px;padding:14px 16px;background:var(--surface)}
.tile .n{font-family:var(--display);font-size:30px;color:var(--ink);line-height:1.1}
.tile .l{font-size:14px;color:var(--muted);margin-top:4px;line-height:1.4}
.tile .d{font-size:13px;color:var(--accent);font-weight:700;margin-top:4px}
</style>"""
chart = (style + '<figure class="dumbbell"><div class="scroll">' + "".join(parts) + '</div>' +
         '<figcaption>Share of each type of personal detail Safe Paste hid, before and after the fixes this study led to. '
         'Default settings, 200 made up case notes, 1,491 personal details. Hover a row for the numbers.<span class="swipe"> On a phone, swipe the chart sideways or see the table below.</span></figcaption></figure>')
(OUT / "chart.html").write_text(chart, encoding="utf-8", newline="\n")

# ---- stat tiles (KPI row) ----
tiles = f"""<div class="tiles">
<div class="tile"><div class="n">{A1['direct_details'] + A1['by_group']['Descriptions that identify someone']['total']:,}</div><div class="l">personal details planted in 200 made up case notes</div></div>
<div class="tile"><div class="n">{A1['direct_rate']:g}%</div><div class="l">of direct identifiers hidden automatically</div><div class="d">up from {A0['direct_rate']:g}% before the fixes</div></div>
<div class="tile"><div class="n">{B1['direct_rate']:g}%</div><div class="l">hidden when staff add the client's name to "Always hide"</div></div>
<div class="tile"><div class="n">0 of {A1['by_group']['Descriptions that identify someone']['total']}</div><div class="l">descriptions that identify someone were caught. Only a person catches these</div></div>
</div>"""
(OUT / "tiles.html").write_text(tiles, encoding="utf-8", newline="\n")

# ---- table (accessible view) ----
rows = "".join(
    f"<tr><td>{html.escape(LABEL[g])}</td><td>{A1['by_group'][g]['total']}</td><td>{A0['by_group'][g]['rate']:g}%</td>"
    f"<td><strong>{A1['by_group'][g]['rate']:g}%</strong></td><td>{B1['by_group'][g]['rate']:g}%</td></tr>"
    for g in sorted(groups, key=lambda g: -A1['by_group'][g]['rate']))
table = ('<div class="table-wrap"><table><thead><tr><th>Type of detail</th><th>Tested</th><th>Version 1.0</th>'
         '<th>Version 1.1</th><th>1.1 + client name in "Always hide"</th></tr></thead><tbody>' + rows +
         f"<tr><td><strong>All direct identifiers (names, numbers, dates, places)</strong></td><td>{A1['direct_details']:,}</td><td>{A0['direct_rate']:g}%</td><td><strong>{A1['direct_rate']:g}%</strong></td><td>{B1['direct_rate']:g}%</td></tr>"
         f"<tr><td><strong>Notes with nothing left behind</strong></td><td>200</td><td>{A0['clean_rate']:g}%</td><td><strong>{A1['clean_rate']:g}%</strong></td><td>{B1['clean_rate']:g}%</td></tr>"
         "</tbody></table></div>")
(OUT / "table.html").write_text(table, encoding="utf-8", newline="\n")
print("figures written to", OUT)
