import json
import os
import sys
import re

FOCUS = re.compile(
    r"accounted for|% of (our )?(net |total )?(revenue|sales)|sole source|single source"
    r"|limited number of suppliers|foundr|contract manufactur|assembly and test"
    r"|(largest|significant|major|key) customers?|customers include|suppliers include",
    re.I,
)

def focus(text):
    paragraphs = text.split("\n\n")
    return "\n\n".join(p for p in paragraphs[1:] if FOCUS.search(p))
from pathlib import Path

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI


def extract(cik, company):
    text = focus(Path(f"data/filings/{cik}.txt").read_text())
    prompt = Path("app/prompt.txt").read_text()
    prompt = prompt.replace("{company}", company).replace("{text}", text)

    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    )
    client = AzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        azure_ad_token_provider=token_provider,
        api_version="2024-10-21",
    )
    response = client.chat.completions.create(
        model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        temperature=0,
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}],
    )
    reply = response.choices[0].message.content.strip().removeprefix("```json").removesuffix("```")
    relationships = json.loads(reply)
    for r in relationships:
        r["company"] = company
    return relationships


if __name__ == "__main__":
    cik, company = sys.argv[1], sys.argv[2]
    relationships = extract(cik, company)
    out = Path(f"data/extracted/{cik}.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(relationships, indent=2))
    print(f"Saved {len(relationships)} relationships to {out}")