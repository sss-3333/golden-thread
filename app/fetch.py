import requests

HEADERS = {"User-Agent": "Safaa Sheikh your-email@example.com"}

def latest_10k(cik):
    url = f"https://data.sec.gov/submissions/CIK{cik:010d}.json"
    data = requests.get(url, headers=HEADERS).json()
    recent = data["filings"]["recent"]
    for i, form in enumerate(recent["form"]):
        if form == "10-K":
            accession = recent["accessionNumber"][i].replace("-", "")
            doc = recent["primaryDocument"][i]
            return f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{doc}"

if __name__ == "__main__":
    link = latest_10k(320193)
    print(link)