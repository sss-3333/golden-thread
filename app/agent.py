import json, os, re, sys
from pathlib import Path
from neo4j import GraphDatabase
from parallel import Parallel
from score import key

web = Parallel(api_key=os.environ["PARALLEL_API_KEY"])
db = GraphDatabase.driver(os.environ["NEO4J_URI"], auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"]))

HOPS = 3                    # how far to follow the chain
PER_HOP = 10                # max companies researched per hop, to cap cost
CACHE = Path("data/agent")  # saved research, one file per company
CACHE.mkdir(parents=True, exist_ok=True)

TASK = ("Find the named suppliers and customers of {} in the semiconductor supply chain. "
        "Only include direct supply of products, components, materials or manufacturing services.")

NAME = "The company's most common short name, without legal endings like Inc, Ltd, AG or GmbH, and without extra descriptions in brackets."

SPEC = {"output_schema": {"type": "json", "json_schema": {
    "type": "object",
    "properties": {"relationships": {
        "type": "array",
        "description": "Up to 15 named supplier and customer relationships of the company, each from a different source where possible.",
        "items": {"type": "object", "properties": {
            "supplier": {"type": "string", "description": NAME},
            "customer": {"type": "string", "description": NAME},
            "quote": {"type": "string", "description": "One sentence copied word for word from the source page"},
            "url": {"type": "string", "description": "The page the quote was copied from"}},
            "required": ["supplier", "customer", "quote", "url"], "additionalProperties": False}}},
    "required": ["relationships"], "additionalProperties": False}}}

pages = {}  # url -> page text, so each page is fetched once


def clean(text):
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)  # markdown links -> their text
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", text.lower()).split())


def verified(quote, url):
    # The verifier: plain code, not AI
    if url not in pages:
        try:
            result = web.extract(urls=[url], objective="supplier and customer relationships",
                                 advanced_settings={"full_content": True}).results
            pages[url] = clean(result[0].full_content or "") if result else ""
        except Exception:
            pages[url] = ""  # unreadable page: nothing can be verified against it
    quote = clean(quote)
    return bool(quote) and quote in pages[url]


def company_id(name):
    return key({"counterparty": name, "relationship": ""})[0]


def save(r):
    db.execute_query(
        """MERGE (s:Company {id: $s}) ON CREATE SET s.name = $sn
           MERGE (c:Company {id: $c}) ON CREATE SET c.name = $cn
           MERGE (s)-[x:SUPPLIES]->(c) SET x.quote = $quote, x.source = $url, x.found_by = 'agent'""",
        s=company_id(r["supplier"]), sn=r["supplier"],
        c=company_id(r["customer"]), cn=r["customer"], quote=r["quote"], url=r["url"])


def research(companies):
    # Reuse saved research; start new Task runs for the rest all at once
    results, runs = {}, {}
    for c in companies:
        path = CACHE / f"{company_id(c)}.json"
        if path.exists():
            results[c] = json.loads(path.read_text())
        else:
            runs[c] = web.task_run.create(input=TASK.format(c), task_spec=SPEC, processor="core")
    for c, run in runs.items():
        try:
            out = web.task_run.result(run.run_id, api_timeout=900).output.content["relationships"]
        except Exception as e:
            print(f"FAILED    {c}: {e}")
            continue
        (CACHE / f"{company_id(c)}.json").write_text(json.dumps(out, indent=2))
        results[c] = out
    return results


level, seen, links, rejected = [sys.argv[1]], set(), set(), 0

for hop in range(HOPS):
    seen.update(company_id(c) for c in level)
    found = []
    for company, relationships in research(level).items():
        for r in relationships:
            if verified(r["quote"], r["url"]):
                save(r)
                links.add((company_id(r["supplier"]), company_id(r["customer"])))
                found += [r["supplier"], r["customer"]]
                print(f"VERIFIED  {r['supplier']} -> {r['customer']}")
            else:
                rejected += 1
                print(f"REJECTED  {r['supplier']} -> {r['customer']}  (quote not on {r['url']})")
    nxt = {}
    for c in found:
        if company_id(c) not in seen:
            nxt.setdefault(company_id(c), c)  # one entry per company, however it was named
    level = list(nxt.values())[:PER_HOP]

print(f"\n{len(pages)} sources read, {len(links)} unique links verified, {rejected} rejected")