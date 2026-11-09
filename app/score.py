import json
import re
from pathlib import Path

SUFFIXES = re.compile(r"\b(inc|incorporated|corp|corporation|co|ltd|limited|plc|llc)\b\.?", re.I)
ALIASES = {
    "taiwan semiconductor manufacturing company": "tsmc",
    "taiwan semiconductor manufacturing": "tsmc",
    "samsung electronics": "samsung",
    "micron technology": "micron",
}


def key(relationship):
    name = SUFFIXES.sub("", relationship["counterparty"].lower())
    name = " ".join(re.sub(r"[^a-z0-9 ]", "", name).split())
    return ALIASES.get(name, name), relationship["relationship"].lower()

def score(cik):
    golden = {key(r) for r in json.loads(Path(f"golden/{cik}.json").read_text())}
    extracted = json.loads(Path(f"data/verified/{cik}.json").read_text())
    found = {key(r) for r in extracted}
    return {
        "matched": sorted(golden & found),
        "missed": sorted(golden - found),
        "invented": sorted(found - golden),
        "duplicates": len(extracted) - len(found),
    }


if __name__ == "__main__":
    totals = {"matched": 0, "missed": 0, "invented": 0, "duplicates": 0}
    for path in sorted(Path("golden").glob("*.json")):
        cik = path.stem
        result = score(cik)
        print(f"\n{cik}: {len(result['matched'])} matched, {len(result['missed'])} missed, "
              f"{len(result['invented'])} invented, {result['duplicates']} duplicates")
        for name, rel in result["missed"]:
            print(f"  MISSED   {name} ({rel})")
        for name, rel in result["invented"]:
            print(f"  INVENTED {name} ({rel})")
        for field in ("matched", "missed", "invented"):
            totals[field] += len(result[field])
        totals["duplicates"] += result["duplicates"]

    precision = totals["matched"] / max(totals["matched"] + totals["invented"], 1)
    recall = totals["matched"] / max(totals["matched"] + totals["missed"], 1)
    summary = {**totals, "precision": round(precision, 3), "recall": round(recall, 3)}
    Path("data/score.json").write_text(json.dumps(summary, indent=2))
    print(f"\nTOTAL: precision {precision:.0%}, recall {recall:.0%}, {totals['duplicates']} duplicates")