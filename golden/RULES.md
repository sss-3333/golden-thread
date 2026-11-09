# Golden dataset: rules and process

## What this is

The golden dataset is a small set of filings where a person, not the AI, has recorded the correct supplier and customer relationships. The quality gate compares the AI reader's output against these answers on every prompt or model change, and blocks any change that makes it less accurate or less consistent.

This file defines exactly what counts as a correct answer, and how the answers were produced.

## Why it exists

An automated check needs something trustworthy to compare against. An AI can't reliably grade its own work: using one AI to check another just moves the problem, because the checker can be wrong in the same ways. So the definition of "correct" comes from a human.

I'm not a finance specialist, so these answers don't rely on my judgement. They rely on the written rules below, applied the same way to every filing. Where a case was unclear, I updated the rules rather than guessing.

## How the answers were produced

For each filing in the golden dataset:

1. **Fetch:** `app/fetch.py` saved the customer and supplier paragraphs from the company's latest 10-K to `data/filings/<id>.txt`. This step uses a keyword search, not AI.
2. **Label before the AI runs:** I read and reviewed (`app/review.py`) that file and recorded every relationship that meets the rules below, with the sentence supporting it. I did this before running the AI reader, so its output couldn't influence my answers.
3. **Check for filter misses:** I searched the full 10-K for "customer", "supplier" and the names of companies I'd found, to see whether the keyword filter had dropped anything. Misses are noted as filter problems, not AI problems, and fixed by updating the keywords.
4. **Record unclear cases:** anything that didn't clearly fit a rule was decided by refining the rules, and noted in the change log at the bottom of this file.

## The rules

**Relationships are recorded from the filing company's point of view:** "who are this company's customers and suppliers?"

### Counts as a customer

A named company that buys from the filing company. For example:
- It is named as accounting for a share of revenue
- It is named as buying the company's products or services
- It pays the company licence fees or royalties

### Counts as a supplier

A named company that provides something the filing company depends on. For example:
- Parts, components or materials
- Manufacturing done on the company's behalf (for example a contract manufacturer or chip foundry)
- Services the company relies on to make or deliver its products

### Doesn't count

- **Competitors,** even if named alongside customers
- **Partners** where the filing describes no buying or selling, such as research collaborations or joint marketing
- **Companies mentioned only in passing,** for example as industry examples
- **Unnamed counterparties,** such as "Customer A" or "a large customer"
- **Possible future relationships,** such as "may supply" or "in discussions with"
- **The company's own subsidiaries**

### Edge cases

- **Past relationships:** count only if the filing describes them as current during the year covered.
- **Distributors and resellers:** count as customers, because they buy from the company.
- **The same company named more than once:** record it once per relationship type, using the clearest supporting sentence.
- **A company that is both a customer and a supplier:** record both relationships separately.

## Answer format

Answers are stored in `golden/<id>.json`, one file per filing, using the same format the AI reader returns:

    [
      {
        "company": "Qualcomm",
        "counterparty": "Apple",
        "relationship": "customer",
        "quote": "The exact sentence from the filing that supports this relationship."
      }
    ]

- `company`: the filing company
- `counterparty`: the other company
- `relationship`: `customer` or `supplier`, describing what the counterparty is to the filing company
- `quote`: the supporting sentence, copied exactly from `data/filings/<id>.txt`

## How it's used

- **Accuracy:** the AI's relationships are compared with these answers, to count how many it got right, how many it invented, and how many it missed.
- **Consistency:** the AI reader runs on each golden filing 3 times, to measure how often it returns the same relationships.
- **The quality gate:** if either score drops after a prompt or model change, CI blocks the change and the live version keeps running.

The human effort is small and only happens once: these answers are saved and reused to test every future change automatically.

## In production

For this project I built the golden dataset myself. In production, it should be built by domain experts, such as analysts who read filings professionally, using written rules like these. At least two people should label the same filings separately, so their agreement can be measured and the rules tightened where they disagree.

## Maintaining it

- **When the AI fails on a new kind of filing,** that filing is labelled using these rules and added to the dataset, so the test keeps up with real use.
- **When a rule changes,** existing answers are re-checked against it, and the change is recorded below.

## Change log

- Initial rules written before labelling the first filing.