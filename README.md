# Workflow Control Harness

This repository is Wes Jones's operating artifact for Single Grain's Beat Claude General 000 challenge (brief version 2026-07).

The harness turns a small portfolio of automation requests into an inspectable operating decision:

1. Validate whether each request is defined well enough to build safely.
2. Rank valid requests by value, feasibility, risk, and maintenance burden.
3. Gate deployment on ownership, validation, retry, alerting, evidence, and human-review controls.
4. Route incomplete requests to a named review queue instead of pretending they are production ready.
5. Produce both machine-readable JSON and a reviewer-friendly Markdown report.

The included data is synthetic and deliberately contains seeded problems. It does not expose customer, employer, or proprietary data.

## Run It

```bash
python3 src/workflow_control_harness.py \
  --requests data/automation_requests.json \
  --events data/run_events.json \
  --json-output output/portfolio_report.json \
  --markdown-output output/portfolio_report.md

python3 -m unittest discover -s tests -v
```

Expected result: the report identifies the strongest build candidate, blocks unsafe deployment candidates, and explains every decision in plain language.

## Review Path

- Start with [`SUBMISSION.md`](SUBMISSION.md).
- Inspect the generated decision report in [`output/portfolio_report.md`](output/portfolio_report.md).
- Review the synthetic inputs in [`data/automation_requests.json`](data/automation_requests.json) and [`data/run_events.json`](data/run_events.json).
- Inspect the implementation in [`src/workflow_control_harness.py`](src/workflow_control_harness.py).
- Run the tests in [`tests/test_workflow_control_harness.py`](tests/test_workflow_control_harness.py).

## Design Boundary

AI can help summarize a request, propose mappings, draft transformations, or classify an exception. It should not silently approve access, release high-impact actions, erase failed runs, or convert an ambiguous request into an autonomous production workflow. The harness keeps those decisions explicit and reviewable.

