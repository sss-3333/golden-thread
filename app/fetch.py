import os
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": os.environ["SEC_USER_AGENT"]}
KEYWORDS = re.compile(r"customer|supplier|sole source|single source|% of (our )?(net |total )?(revenue|sales)", re.I)


def latest_10k(cik):
    url = f"https://data.sec.gov/submissions/CIK{cik:010d}.json"
    data = requests.get(url, headers=HEADERS).json()
    recent = data["filings"]["recent"]
    for i, form in enumerate(recent["form"]):
        if form == "10-K":
            accession = recent["accessionNumber"][i].replace("-", "")
            doc = recent["primaryDocument"][i]
            return f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{doc}"


def relevant_paragraphs(url):
    html = requests.get(url, headers=HEADERS).text
    soup = BeautifulSoup(html, "html.parser")
    blocks = [el for el in soup.find_all(["p", "div"]) if not el.find(["p", "div"])]
    paragraphs = [" ".join(el.get_text(" ").split()) for el in blocks]
    return [p for p in paragraphs if len(p) > 80 and KEYWORDS.search(p)]


if __name__ == "__main__":
    cik = int(sys.argv[1])
    url = latest_10k(cik)
    paragraphs = relevant_paragraphs(url)
    out = Path("data/filings") / f"{cik}.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(f"SOURCE: {url}\n\n" + "\n\n".join(paragraphs))
    print(url)
    print(f"{len(paragraphs)} relevant paragraphs saved to {out}")