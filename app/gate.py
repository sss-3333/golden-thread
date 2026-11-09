import json
import sys
from pathlib import Path

baseline = json.loads(Path("results/baseline.json").read_text())
current = json.loads(Path("data/score.json").read_text())

failed = False
for metric in ("precision", "recall"):
    passed = current[metric] >= baseline[metric]
    failed = failed or not passed
    print(f"{'PASS' if passed else 'FAIL'} {metric}: {current[metric]:.0%} (baseline {baseline[metric]:.0%})")
print(f"duplicates: {current['duplicates']} (baseline {baseline['duplicates']})")

sys.exit(1 if failed else 0)