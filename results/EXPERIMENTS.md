# Findings

**The question:** how do you make AI-generated knowledge verifiable, measurable and maintainable as models and prompts change?

**Setup:** 5 SEC 10-K filings · 66 hand-checked relationships · `gpt-4.1-mini` on Azure OpenAI · temperature 0

---

## Baseline

| Precision | Recall | Duplicates |
|:---:|:---:|:---:|
| **100%** | **97%** (64 of 66) | **1** |

---

## Version history

| Version | Change | Precision | Recall | Duplicates |
|---|---|---|---|:---:|
| **v1** | First prompt, first golden set | `████████░░` 84% | `███████░░░` 78% | 10 |
| **v2** | Golden set: added 5 Cirrus Logic suppliers I'd missed | `█████████░` 93% | `████████░░` 80% | 10 |
| **v3** | **Prompt:** AI no longer returns the filing company | `█████████░` 92% | `█████████░` 91% | 1 |
| **v4** | Golden set: Micron added, names standardised, alternative names in scoring | `██████████` 100% | `██████████` 97% | 1 |

- **v1 → v2 and v3 → v4** fixed the **test**.
- **v2 → v3** improved the **AI**. One prompt change took Qualcomm from **0 to 7 matched** and duplicates from **10 to 1**.

---

## Three kinds of error

| What happened | Cause | Who was wrong | Fix |
|---|---|---|---|
| Same suppliers counted as missed *and* invented (NVIDIA) | "TSMC" vs "Taiwan Semiconductor Manufacturing Company" | Neither | Naming rule + alternative names in scoring |
| 5 suppliers counted as invented (Cirrus Logic) | Genuine relationships I missed while labelling | Me | Checked against the rules, added, logged |
| All 10 relationships pointed the wrong way (Qualcomm) | Prompt asked the AI for the filing company, and it swapped the fields | Prompt design | Script adds the filing company + reject self-relationships |

---

## Key findings

1. **AI is confidently wrong.** The swapped Qualcomm relationships looked as certain as the correct ones. The AI never flagged a mistake.
2. **One check isn't enough.** The quote check passed all 10 swapped relationships, because the quotes were real. Only the golden comparison caught them.
3. **Errors depend on the input.** The same prompt worked on NVIDIA and failed on Qualcomm. Testing on one or two files would have missed it.
4. **The test can be wrong too.** The AI found 6 relationships I'd missed. The golden set needs a fair correction process, not blind trust.
5. **97% recall isn't enough.** Both misses were significant: **Xiaomi** (Qualcomm customer) and the **US Government** (Qorvo customer). Both sentences were sent to the AI, so these are AI misses, not filter misses.
6. **Experiment: vague prompt.** Replaced the prompt with "List the companies that {company} works with", with no definitions, naming rule or quoting rule. Precision fell from 100% to 80% and recall from 97% to 30%. The gate failed both checks. This prompt is kept as the demo for the gate blocking a pull request.

---

## How this answers the question

| | How | Evidence |
|---|---|---|
| **Verifiable** | Every relationship carries an exact quote, checked against the filing | 0 invented quotes across all runs |
| **Measurable** | Precision, recall and duplicates against a human-checked golden set | Four versions scored, from 84%/78% to 100%/97% |
| **Maintainable** | Every prompt or model change is re-scored before it ships | The v3 prompt fix measured, not guessed |

---

## Next

- **Critical relationships:** flag major customers and sole suppliers in the golden set, and fail the gate if any are missed, whatever the average
- **Held-out set:** extra filings never used for tuning, to check improvements aren't tailored to these 5
- **Second model:** run Claude through the same golden set to compare accuracy and cost

---

## Reproduce any version

```bash
git checkout v1          # or v3, v4-baseline
python app/score.py      # scores that version's saved AI output, no API calls
git checkout main
```

**Limits:** 5 filings and one model, so these scores catch regressions rather than guarantee accuracy at scale.
