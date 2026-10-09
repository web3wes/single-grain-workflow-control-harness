# Automation Portfolio Report

All data in this report is synthetic.

## Summary

- [Observed] Requests inspected: 5
- [Observed] Production-ready requests: 4
- [Observed] Requests routed to design review: 1
- [Observed] Run events routed to the human exception queue: 2

## Portfolio Decisions

| Rank | Request | Score | Production ready | Decision | Missing controls | Source label |
|---:|---|---:|---|---|---|---|
| 1 | REQ-001: Client reporting narrative draft | 11.33 | true | eligible_for_build_queue | none | [Observed] synthetic fixture |
| 2 | REQ-002: Lead-source normalization | 10.5 | true | eligible_for_build_queue | none | [Observed] synthetic fixture |
| 3 | REQ-005: Meeting-action extraction and routing | 9.2 | true | eligible_for_build_queue | none | [Observed] synthetic fixture |
| 4 | REQ-004: Publish AI-generated client recommendations | 2.83 | false | route_to_design_review | alert_route, evidence_sink, human_approval_required_for_high_risk_action, retry_limit, validation_rule | [Observed] synthetic fixture |
| 5 | REQ-003: Automatic campaign budget changes | 2.7 | true | eligible_for_build_queue | none | [Observed] synthetic fixture |

## Run Findings

| Run | Request | Route | Issues | Source label |
|---|---|---|---|---|
| RUN-1001 | REQ-001 | complete | none | [Observed] synthetic fixture |
| RUN-1002 | REQ-002 | complete | none | [Observed] synthetic fixture |
| RUN-1003 | REQ-003 | human_exception_queue | run_failed, validation_missing_or_failed | [Observed] synthetic fixture |
| RUN-1004 | REQ-005 | human_exception_queue | evidence_not_written | [Observed] synthetic fixture |

## Operating Decision

A high priority score does not authorize deployment. Requests enter the build queue only after the production-readiness gate passes. Failed validation, missing evidence, or missing required approval routes a run to a human exception queue.
