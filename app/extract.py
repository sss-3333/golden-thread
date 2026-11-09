import json
import re
import sys
from pathlib import Path

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI

CONFIG = json.loads(Path("app/config.json").read_text())

FOCUS = re.compile(
    r"accounted for|% of (our )?(net |total )?(revenue|sales)|sole source|single source"
    r"|limited number of suppliers|foundr|contract manufactur|assembly and test"
    r"|(largest|significant|major|key) customers?|customers include|suppliers include",
    re.I,
)


def focus(text):
    paragraphs = text.split("\n\n")
    return "\n\n".join(p for p in paragraphs[1:] if FOCUS.search(p))


def extract(cik, company):
    text = focus(Path(f"data/filings/{cik}.txt").read_text())
    prompt = Path("app/prompt.txt").read_text()
    prompt = prompt.replace("{company}", company).replace("{text}", text)

    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    )
    client = AzureOpenAI(
        azure_endpoint=CONFIG["endpoint"],
        azure_ad_token_provider=token_provider,
        api_version=CONFIG["api_version"],
        max_retries=5,
    )
    response = client.chat.completions.create(
        model=CONFIG["deployment"],
        temperature=0,
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )
    reply = response.choices[0].message.content.strip().removeprefix("```json").removesuffix("```")
    relationships = json.loads(reply)
    for r in relationships:
        r["company"] = company
    return relationships


def save(cik, company):
    relationships = extract(cik, company)
    out = Path(f"data/extracted/{cik}.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(relationships, indent=2))
    print(f"{cik} ({company}): {len(relationships)} relationships")


if __name__ == "__main__":
    if len(sys.argv) == 3:
        save(sys.argv[1], sys.argv[2])
    else:
        for path in sorted(Path("golden").glob("*.json")):
            save(path.stem, json.loads(path.read_text())[0]["company"])