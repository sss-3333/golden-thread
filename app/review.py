import json
import re
import sys
from pathlib import Path

ABBREV = re.compile(r"\b(Inc|Ltd|Co|Corp|Cos|No|vs|St)\.$")
SUFFIX = re.compile(r"\b(Inc|Corp|Corporation|Ltd|Limited|Co|Company|LLC|plc|N\.V|S\.A|AG|GmbH)\b\.?")
CAPS = re.compile(r"\b[A-Z]{3,}\b")
MIDCAP = re.compile(r"(?<![.!?•]\s)(?<!^)\b[A-Z][a-z]+[A-Z]?\w*")
SKIP = {"We", "Our", "The", "If", "In", "As", "For", "This", "These", "Some", "Any", "Item", "Part"}


def split_sentences(text):
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z•“\"(])", text)
    out = []
    for p in parts:
        if out and ABBREV.search(out[-1]):
            out[-1] += " " + p
        else:
            out.append(p)
    return out


def mentions_company(s):
    if SUFFIX.search(s) or CAPS.search(s):
        return True
    words = s.split()
    return any(w.strip(",.;:()\"'") [:1].isupper() and w.strip(",.;:()\"'") not in SKIP for w in words[1:])


def main(filing_id, company):
    text = Path(f"data/filings/{filing_id}.txt").read_text()
    out = Path(f"golden/{filing_id}.json")
    records = json.loads(out.read_text()) if out.exists() else []
    done = {r["quote"] for r in records}
    paragraphs = text.split("\n\n")[1:]
    for para in paragraphs:
        for s in split_sentences(para):
            s = s.strip()
            if not 40 <= len(s) <= 800 or s in done or not mentions_company(s):
                continue
            print("\n" + s)
            while True:
                a = input("y/n/q: ").strip().lower()
                if a in ("y", "n", "q"):
                    break
            if a == "q":
                out.write_text(json.dumps(records, indent=2, ensure_ascii=False))
                return
            if a == "n":
                continue
            while True:
                counterparty = input("counterparty (blank to cancel): ").strip()
                if not counterparty:
                    break
                rel = input("customer or supplier: ").strip().lower()
                if rel in ("c", "customer"):
                    rel = "customer"
                elif rel in ("s", "supplier"):
                    rel = "supplier"
                else:
                    print("type customer or supplier")
                    continue
                assert s in text
                records.append({"company": company, "counterparty": counterparty, "relationship": rel, "quote": s})
                out.write_text(json.dumps(records, indent=2, ensure_ascii=False))
                if input("another company in this sentence? y/n: ").strip().lower() != "y":
                    break
    out.write_text(json.dumps(records, indent=2, ensure_ascii=False))
    print(f"done, {len(records)} relationships in {out}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])