# Redaction study: 200 made up case notes

Original study behind the post [We tested 200 case notes on our own redaction tool](https://safeaifornonprofits.ca/blog/redaction-study-200-case-notes/).

- `notes.jsonl`: 200 made up case notes (case notes, emails, referrals, texting style; Ontario, BC, UK, US) with 1,491 planted personal details, each with its exact position. Everything is fake by construction (555-01xx phones, NHS test range, SINs starting with 0, SSNs starting with 9, example.org emails).
- `make_notes.py`: rebuilds the set (seeded, so it's identical every time).
- `run.mjs`: runs every note through Safe Paste's real detection code in a browser. Scenario A = default settings, B = the client's name added to "Always hide".
- `analyze.py`: strict scoring. Caught = every non-space character hidden; partial hides count as misses. A note is clean only if every direct identifier is hidden.
- `results_v1.0.json`, `results_v1.1.json`: scores before and after the fixes this study led to. `detections_*.json`: raw output. `results_by_kind.csv`, `misses.csv`: latest version, per kind and every miss.
- `make_figures.py`: the chart, stat tiles and table used in the post.

Reproduce:

```bash
python research/make_notes.py
node research/run.mjs v1.1
python research/analyze.py v1.1
```

Headline (v1.1): 89.4% of 1,451 direct identifiers hidden by default, 95.3% with the client's name in "Always hide"; 45% / 66% of notes fully clean; 0 of 40 identifying descriptions caught; 0 false alarms on this set (which has few capitalized non-names, so expect some in real notes).

Want to test another tool on the same set? Use `notes.jsonl` and the scoring in `analyze.py`, and please share what you find.
