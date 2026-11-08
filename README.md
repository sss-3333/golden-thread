# Golden Thread

A supply-chain knowledge graph built by checked AI, with live event alerts.

## Why I built this

AI tools that read documents can quietly get less accurate when someone changes a prompt or model. The output still looks confident, so nobody notices until it matters.

## What it does

- **Supply-chain knowledge graph:** maps which companies supply which, so you can see who is exposed when one company has a problem.
- **AI reader:** reads the supplier and customer sections of SEC annual filings (10-Ks) and extracts each relationship, along with the exact sentence it came from.
- **Quote check:** confirms every quoted sentence really exists in the filing, and rejects any link where it doesn't.
- **Quality gate:** scores the AI reader against a golden dataset of hand-checked filings. Any prompt or model change that lowers the score is blocked in CI, so the live version stays running until the change is fixed.
- **Live event alerts:** watches the SEC's 8-K feed and flags when something important happens to a company in the graph, plus which companies depend on it.
- **AI assistant:** an MCP server that lets an AI assistant answer plain-English questions about how companies depend on each other, citing the source of each connection. Optionally connected to a Copilot Studio agent.

## Golden dataset

A small set of filings (starting with 5) where I read the supplier and customer sections myself and wrote down every relationship before looking at the AI's output. It's a one-off manual step, reused on every change. The score is indicative, not definitive. Its main job is catching regressions.

## Platform

- **Infrastructure:** AKS, built with Terraform, reusing my Trackance platform code
- **Deployment:** GitOps with ArgoCD
- **CI:** image builds, security scanning, and the quality gate
- **Storage:** Neo4j for the graph, with backups
- **Scheduled jobs:** filing collection and 8-K event checks
- **Monitoring:** Prometheus and Grafana for health, alerts, and AI cost per filing

## Limitations

- Filings only name major customers and suppliers, so the graph shows significant relationships, not every one.
- A small golden dataset gives a rough accuracy score, not a guarantee across all filings.
- The finance logic is deliberately simple. The focus is the reliability and trust around the AI.

## Status

- [ ] Fetch filings from SEC EDGAR
- [ ] AI reader with quoted sources
- [ ] Quote check
- [ ] Golden dataset and quality gate in CI
- [ ] Neo4j graph
- [ ] Live event alerts (8-K feed)
- [ ] AI assistant (MCP)
- [ ] Platform on AKS with GitOps
- [ ] Monitoring and cost tracking