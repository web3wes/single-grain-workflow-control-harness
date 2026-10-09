#!/usr/bin/env python3
"""Rank automation opportunities and gate them for production readiness."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = (
    "id",
    "name",
    "owner",
    "frequency_per_month",
    "minutes_per_run",
    "error_cost",
    "feasibility",
    "risk",
    "maintenance_burden",
    "validation_rule",
    "retry_limit",
    "alert_route",
    "evidence_sink",
    "human_approval_required",
)


def load_json(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON list")
    return data


def missing_controls(request: dict[str, Any]) -> list[str]:
    missing = [field for field in REQUIRED_FIELDS if field not in request]
    for field in ("owner", "validation_rule", "alert_route", "evidence_sink"):
        if field in request and not str(request[field]).strip():
            missing.append(field)
    if request.get("retry_limit", 0) < 1:
        missing.append("retry_limit")
    if request.get("risk", 0) >= 4 and not request.get("human_approval_required"):
        missing.append("human_approval_required_for_high_risk_action")
    return sorted(set(missing))


def priority_score(request: dict[str, Any]) -> float:
    monthly_hours = request["frequency_per_month"] * request["minutes_per_run"] / 60
    value = min(monthly_hours / 10, 10) + request["error_cost"]
    delivery = request["feasibility"] * 2
    penalty = request["risk"] * 1.5 + request["maintenance_burden"]
    return round(value + delivery - penalty, 2)


def inspect_event(event: dict[str, Any], requests_by_id: dict[str, dict[str, Any]]) -> list[str]:
    issues: list[str] = []
    request = requests_by_id.get(event.get("request_id"))
    if request is None:
        return ["unknown_request"]
    if event.get("status") != "success":
        issues.append("run_failed")
    if not event.get("validated"):
        issues.append("validation_missing_or_failed")
    if not event.get("evidence_written"):
        issues.append("evidence_not_written")
    if request.get("human_approval_required") and not event.get("approval_recorded"):
        issues.append("required_approval_missing")
    return issues


def build_report(requests: list[dict[str, Any]], events: list[dict[str, Any]]) -> dict[str, Any]:
    requests_by_id = {request["id"]: request for request in requests if "id" in request}
    portfolio: list[dict[str, Any]] = []
    for request in requests:
        missing = missing_controls(request)
        portfolio.append(
            {
                "id": request.get("id", "unknown"),
                "name": request.get("name", "unnamed"),
                "priority_score": priority_score(request) if not any(
                    field not in request for field in REQUIRED_FIELDS
                ) else None,
                "production_ready": not missing,
                "missing_controls": missing,
                "decision": "eligible_for_build_queue" if not missing else "route_to_design_review",
            }
        )
    portfolio.sort(key=lambda item: item["priority_score"] or float("-inf"), reverse=True)

    event_findings = []
    for event in events:
        issues = inspect_event(event, requests_by_id)
        event_findings.append(
            {
                "run_id": event.get("run_id", "unknown"),
                "request_id": event.get("request_id", "unknown"),
                "issues": issues,
                "route": "human_exception_queue" if issues else "complete",
            }
        )

    return {
        "portfolio": portfolio,
        "run_findings": event_findings,
        "summary": {
            "request_count": len(requests),
            "production_ready_count": sum(item["production_ready"] for item in portfolio),
            "blocked_count": sum(not item["production_ready"] for item in portfolio),
            "exception_run_count": sum(bool(item["issues"]) for item in event_findings),
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Automation Portfolio Report",
        "",
        "All data in this report is synthetic.",
        "",
        "## Summary",
        "",
        f"- [Observed] Requests inspected: {summary['request_count']}",
        f"- [Observed] Production-ready requests: {summary['production_ready_count']}",
        f"- [Observed] Requests routed to design review: {summary['blocked_count']}",
        f"- [Observed] Run events routed to the human exception queue: {summary['exception_run_count']}",
        "",
        "## Portfolio Decisions",
        "",
        "| Rank | Request | Score | Production ready | Decision | Missing controls | Source label |",
        "|---:|---|---:|---|---|---|---|",
    ]
    for rank, item in enumerate(report["portfolio"], 1):
        missing = ", ".join(item["missing_controls"]) or "none"
        lines.append(
            f"| {rank} | {item['id']}: {item['name']} | {item['priority_score']} | "
            f"{str(item['production_ready']).lower()} | {item['decision']} | {missing} | [Observed] synthetic fixture |"
        )
    lines.extend(
        [
            "",
            "## Run Findings",
            "",
            "| Run | Request | Route | Issues | Source label |",
            "|---|---|---|---|---|",
        ]
    )
    for item in report["run_findings"]:
        issues = ", ".join(item["issues"]) or "none"
        lines.append(
            f"| {item['run_id']} | {item['request_id']} | {item['route']} | {issues} | [Observed] synthetic fixture |"
        )
    lines.extend(
        [
            "",
            "## Operating Decision",
            "",
            "A high priority score does not authorize deployment. Requests enter the build queue only after the production-readiness gate passes. Failed validation, missing evidence, or missing required approval routes a run to a human exception queue.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--requests", type=Path, required=True)
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--markdown-output", type=Path, required=True)
    args = parser.parse_args()

    report = build_report(load_json(args.requests), load_json(args.events))
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    args.markdown_output.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps(report["summary"], sort_keys=True))


if __name__ == "__main__":
    main()

