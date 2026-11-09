import json
from pathlib import Path

REPLACEMENTS = {"\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"'}


def normalise(text):
    for curly, straight in REPLACEMENTS.items():
        text = text.replace(curly, straight)
    return " ".join(text.split())


def verify(cik):
    filing = normalise(Path(f"data/filings/{cik}.txt").read_text())
    extracted = json.loads(Path(f"data/extracted/{cik}.json").read_text())
    verified = [r for r in extracted if normalise(r["quote"]) in filing and r["counterparty"].lower() != r["company"].lower()]
    rejected = [r for r in extracted if r not in verified]
    return verified, rejected


if __name__ == "__main__":
    for path in sorted(Path("data/extracted").glob("*.json")):
        cik = path.stem
        verified, rejected = verify(cik)
        out = Path(f"data/verified/{cik}.json")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(verified, indent=2))
        print(f"{cik}: {len(verified)} verified, {len(rejected)} rejected")
        for r in rejected:
            print(f"  REJECTED {r['counterparty']}: {r['quote'][:100]}")