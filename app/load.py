import json
import os
from pathlib import Path

from neo4j import GraphDatabase

from score import key

QUERY = """
MERGE (s:Company {id: $supplier_id}) ON CREATE SET s.name = $supplier
MERGE (b:Company {id: $buyer_id}) ON CREATE SET b.name = $buyer
MERGE (s)-[r:SUPPLIES]->(b)
SET r.quote = $quote, r.source = $source, r.reported_by = $reported_by
"""


def company_id(name):
    return key({"counterparty": name, "relationship": ""})[0]


def source_url(cik):
    first_line = Path(f"data/filings/{cik}.txt").read_text().splitlines()[0]
    return first_line.removeprefix("SOURCE: ")


if __name__ == "__main__":
    driver = GraphDatabase.driver(
        os.environ["NEO4J_URI"], auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"])
    )
    count = 0
    with driver.session() as session:
        for path in sorted(Path("data/verified").glob("*.json")):
            source = source_url(path.stem)
            for r in json.loads(path.read_text()):
                if r["relationship"] == "supplier":
                    supplier, buyer = r["counterparty"], r["company"]
                else:
                    supplier, buyer = r["company"], r["counterparty"]
                session.run(
                    QUERY,
                    supplier=supplier, supplier_id=company_id(supplier),
                    buyer=buyer, buyer_id=company_id(buyer),
                    quote=r["quote"], source=source, reported_by=r["company"],
                )
                count += 1
    driver.close()
    print(f"Loaded {count} relationships")