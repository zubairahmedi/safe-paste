"""Scores the detections against the ground truth.

    python research/analyze.py v1.1   -> research/results_v1.1.json (+ results_by_kind.csv, misses.csv for that version)

A detail counts as caught only if every non-space character of it is inside something Safe Paste hid.
A partial hide counts as a miss (half a phone number still leaks).
A false alarm is something Safe Paste hid that isn't a personal detail.
"""
import csv
import json
import pathlib
import sys
from collections import defaultdict

HERE = pathlib.Path(__file__).resolve().parent
VER = sys.argv[1] if len(sys.argv) > 1 else "v1.1"
notes = [json.loads(l) for l in (HERE / "notes.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
det = {d["id"]: d for d in json.loads((HERE / f"detections_{VER}.json").read_text(encoding="utf-8"))}


def covered(text, ent, spans):
    need = [i for i in range(ent["start"], ent["end"]) if not text[i].isspace()]
    hit = [i for i in need if any(s <= i < e for s, e, *_ in spans)]
    return "caught" if len(hit) == len(need) else ("partial" if hit else "missed")


def score(scn):
    by_kind = defaultdict(lambda: {"caught": 0, "partial": 0, "missed": 0, "group": ""})
    by_group = defaultdict(lambda: {"caught": 0, "total": 0})
    misses, false_alarms = [], []
    clean_notes, total_direct, caught_direct = 0, 0, 0
    for n in notes:
        spans = det[n["id"]][scn]
        clean = True
        for e in n["entities"]:
            r = covered(n["text"], e, spans)
            k = by_kind[e["kind"]]
            k[r] += 1
            k["group"] = e["group"]
            by_group[e["group"]]["total"] += 1
            by_group[e["group"]]["caught"] += r == "caught"
            if e["group"] != "Descriptions that identify someone":
                total_direct += 1
                caught_direct += r == "caught"
                if r != "caught":
                    clean = False
            if r != "caught":
                misses.append({"note": n["id"], "kind": e["kind"], "result": r, "value": e["value"]})
        clean_notes += clean
        for s, e, typ, sure in spans:
            if not any(s < x["end"] and x["start"] < e for x in n["entities"]):
                false_alarms.append({"note": n["id"], "hidden_as": typ, "value": n["text"][s:e], "sure": sure})
    return {
        "notes": len(notes), "direct_details": total_direct, "direct_caught": caught_direct,
        "direct_rate": round(100 * caught_direct / total_direct, 1),
        "clean_notes": clean_notes, "clean_rate": round(100 * clean_notes / len(notes), 1),
        "false_alarms": len(false_alarms),
        "by_group": {g: {**v, "rate": round(100 * v["caught"] / v["total"], 1)} for g, v in by_group.items()},
        "by_kind": {k: {**v, "total": v["caught"] + v["partial"] + v["missed"],
                        "rate": round(100 * v["caught"] / (v["caught"] + v["partial"] + v["missed"]), 1)} for k, v in by_kind.items()},
        "misses": misses, "false_alarm_list": false_alarms,
    }


res = {"A_default": score("A"), "B_name_in_always_hide": score("B")}
(HERE / f"results_{VER}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
with (HERE / "results_by_kind.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["kind", "group", "total", "caught_default", "rate_default", "partial_default", "caught_with_name_added", "rate_with_name_added"])
    a, b = res["A_default"]["by_kind"], res["B_name_in_always_hide"]["by_kind"]
    for k in sorted(a, key=lambda k: a[k]["rate"]):
        w.writerow([k, a[k]["group"], a[k]["total"], a[k]["caught"], a[k]["rate"], a[k]["partial"], b[k]["caught"], b[k]["rate"]])
with (HERE / "misses.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["note", "kind", "result", "value"])
    w.writeheader()
    w.writerows(res["A_default"]["misses"])

for scn, r in res.items():
    print(f"\n== {scn} ==  details caught {r['direct_caught']}/{r['direct_details']} ({r['direct_rate']}%), "
          f"fully clean notes {r['clean_notes']}/{r['notes']} ({r['clean_rate']}%), false alarms {r['false_alarms']}")
    for g, v in sorted(r["by_group"].items(), key=lambda x: x[1]["rate"]):
        print(f"  {v['rate']:5.1f}%  {v['caught']:4d}/{v['total']:<4d} {g}")
a = res["A_default"]
print("\nkinds below 100% (default):")
for k, v in sorted(a["by_kind"].items(), key=lambda x: x[1]["rate"]):
    if v["rate"] < 100:
        print(f"  {v['rate']:5.1f}%  {k:24s} caught {v['caught']}/{v['total']} partial {v['partial']}")
print("\nfalse alarms (default):")
from collections import Counter
print(Counter(f["value"] for f in a["false_alarm_list"]).most_common(25))
