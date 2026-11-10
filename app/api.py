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
RETURN s.name AS name, r.quote AS quote, r.source AS source ORDER BY name
"""
CUSTOMERS = """
MATCH (:Company {id: $id})-[r:SUPPLIES]->(c)
RETURN c.name AS name, r.quote AS quote, r.source AS source ORDER BY name
"""


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


@app.get("/livez")
def livez():
    return {"status": "ok"}


@app.get("/readyz")
def readyz():
    driver.verify_connectivity()
    return {"status": "ok"}