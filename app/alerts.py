import json
import os
from itertools import islice
from pathlib import Path
import requests
from neo4j import GraphDatabase
from score import key

HEADERS = {"User-Agent": os.environ["SEC_USER_AGENT"]}
SAVE = """
MATCH (c:Company {id: $company})
MERGE (e:Event {url: $url})
SET e.date = $date, e.items = $items
MERGE (c)-[:FILED]->(e)
"""


def recent_8ks(cik):
    url = f"https://data.sec.gov/submissions/CIK{int(cik):010d}.json"
    recent = requests.get(url, headers=HEADERS).json()["filings"]["recent"]
    for i, form in enumerate(recent["form"]):
        if form == "8-K":
            accession = recent["accessionNumber"][i].replace("-", "")
            yield {
                "date": recent["filingDate"][i],
                "items": recent["items"][i],
                "url": f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/{recent['primaryDocument'][i]}",
            }


driver = GraphDatabase.driver(
    os.environ["NEO4J_URI"],
    auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"]),
)
saved = 0
with driver.session() as session:
    for path in sorted(Path("data/verified").glob("*.json")):
        name = json.loads(Path(f"golden/{path.stem}.json").read_text())[0]["company"]
        company = key({"counterparty": name, "relationship": ""})[0]
        for event in islice(recent_8ks(path.stem), 5):
            session.run(SAVE, company=company, **event)
            saved += 1
print(f"Saved {saved} events")