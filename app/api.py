import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from neo4j import GraphDatabase
from score import key

driver = GraphDatabase.driver(
    os.environ["NEO4J_URI"],
    auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"]),
)
app = FastAPI()
PAGE = (Path(__file__).parent / "index.html").read_text()

SUPPLIERS = """
MATCH (s)-[r:SUPPLIES]->(:Company {id: $id})
RETURN s.name AS name, r.quote AS quote, r.source AS source, r.found_by AS found_by ORDER BY name
"""
CUSTOMERS = """
MATCH (:Company {id: $id})-[r:SUPPLIES]->(c)
RETURN c.name AS name, r.quote AS quote, r.source AS source, r.found_by AS found_by ORDER BY name
"""
ALERTS = """
MATCH (c:Company)-[:FILED]->(e:Event)
OPTIONAL MATCH (c)-[:SUPPLIES]-(n)
WITH c, e, collect(DISTINCT n) AS partners
WHERE $id IS NULL OR c.id = $id OR any(p IN partners WHERE p.id = $id)
RETURN c.name AS company, e.date AS date, e.items AS items, e.url AS url,
       [p IN partners | p.name] AS affected
ORDER BY date DESC LIMIT 10
"""
ITEMS = {
    "1.01": "new major agreement",
    "1.02": "major agreement ended",
    "1.05": "cybersecurity incident",
    "2.01": "acquisition or sale",
    "2.02": "results",
    "2.05": "restructuring",
    "5.02": "leadership change",
    "5.07": "shareholder vote",
    "7.01": "investor disclosure",
    "8.01": "other event",
    "9.01": "financial statements",
}

@app.get("/", response_class=HTMLResponse)
def page():
    return PAGE


@app.get("/api/companies/{name}")
def company(name: str):
    company_id = key({"counterparty": name, "relationship": ""})[0]
    with driver.session() as session:
        suppliers = session.run(SUPPLIERS, id=company_id).data()
        customers = session.run(CUSTOMERS, id=company_id).data()
    if not suppliers and not customers:
        raise HTTPException(404, "Company not found")
    return {"suppliers": suppliers, "customers": customers}

@app.get("/api/alerts")
def alerts(company: str | None = None):
    company_id = key({"counterparty": company, "relationship": ""})[0] if company else None
    with driver.session() as session:
        rows = session.run(ALERTS, id=company_id).data()
    for row in rows:
        codes = row.pop("items").split(",")
        row["event"] = ", ".join(ITEMS.get(code, code) for code in codes if code)
    return rows

@app.get("/livez")
def livez():
    return {"status": "ok"}


@app.get("/readyz")
def readyz():
    driver.verify_connectivity()
    return {"status": "ok"}