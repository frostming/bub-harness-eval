"""Summarize canonical task evidence without substituting zeros for missing data."""
import json
import statistics
import sys
from pathlib import Path

run = Path(sys.argv[1])
candidate = json.loads((run / "candidate.json").read_text())
tasks = []
for item in candidate["task_details"]:
    evidence = run / item.get("evidence", "") / "trial.json"
    raw = json.loads(evidence.read_text()) if evidence.is_file() else {}
    tasks.append({**raw, **item})
valid = [t for t in tasks if t.get("status") in ("success", "failure")]
measured = [t for t in tasks if t.get("input_tokens") is not None and t.get("output_tokens") is not None]
costs = [t["cost_first_cold_usd"] for t in tasks if t.get("cost_first_cold_usd") is not None]
observed_path = run / "observed-cost-audit.json"
observed = json.loads(observed_path.read_text()) if observed_path.is_file() else {}
observed_by_task = {t["task"]: t for t in observed.get("tasks", [])}
available_costs = []
for task in tasks:
    value = task.get("cost_first_cold_usd")
    if value is None:
        value = observed_by_task.get(task["id"], {}).get("observed_cost_usd")
    if value is not None:
        available_costs.append(value)
durations = [t["duration_seconds"] for t in valid if t.get("duration_seconds") is not None]
summary = {
    "run_id": run.name,
    "expected_tasks": candidate["expected"],
    "valid_tasks": len(valid),
    "passed_tasks": sum(t.get("success") is True for t in valid),
    "infrastructure_invalid": [t["id"] for t in tasks if t.get("status") == "infra_invalid"],
    "missing_tasks": sum(t.get("status") == "missing" for t in tasks),
    "input_tokens_measured": sum(t["input_tokens"] for t in measured) if measured else None,
    "output_tokens_measured": sum(t["output_tokens"] for t in measured) if measured else None,
    "token_measured_tasks": len(measured),
    "model_calls_measured": observed.get("usage_calls", sum(t["turns"] for t in tasks if t.get("turns") is not None)),
    "call_measured_tasks": sum(t.get("usage_calls", 0) > 0 for t in observed.get("tasks", [])) if observed else sum(t.get("turns") is not None for t in tasks),
    "requests_without_complete_usage": observed.get("missing_usage"),
    "available_standardized_cost_usd": sum(available_costs) if available_costs else None,
    "available_cost_measured_tasks": len(available_costs),
    "standardized_first_cold_cost_usd": sum(costs) if costs else None,
    "cost_measured_tasks": len(costs),
    "median_full_runner_seconds_all_valid": statistics.median(durations) if durations else None,
    "median_full_runner_seconds_successes": candidate.get("median_duration_seconds"),
    "actual_provider_bill_usd": None,
    "runtime_charges_usd": None,
    "comparable_to_published_leaderboard": False,
    "notes": [
        "Costs use frozen K3 token rates; they are not Kimi Coding plan billing or Runta charges.",
        "Token and cost totals include measured failures; coverage is explicit and missing values are not zero.",
        "Available cost uses each complete first-cold task cost, or that task's observed-call lower bound once. Observed calls include partial-coverage tasks; missing calls stay unknown.",
        "Latency is full runner wall time, not model response latency; image-pull and restore time are excluded.",
        "A matched control for provider, corpus and isolation conditions has not been established.",
    ],
}
blocker_path = run / "controller" / "provider-blocked.json"
if blocker_path.is_file():
    summary["run_status"] = "incomplete_provider_quota_blocked"
    summary["blocker"] = json.loads(blocker_path.read_text())
else:
    summary["run_status"] = "complete" if len(valid) == candidate["expected"] else "incomplete"
(run / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
def show(value):
    return "Not recorded" if value is None else f"{value:,.2f}" if isinstance(value, float) else f"{value:,}"

markdown = f"""# {candidate.get('label', 'Bub')} evaluation

Run: `{run.name}` · Not ranked against published baselines

Status: **{summary['run_status']}**
{summary.get('blocker', {}).get('reason', '')}

| Measurement | Result |
| --- | --- |
| Passed / valid / expected tasks | {summary['passed_tasks']} / {len(valid)} / {candidate['expected']} |
| Infrastructure-invalid / missing tasks | {len(summary['infrastructure_invalid'])} / {summary['missing_tasks']} |
| Input tokens | {show(summary['input_tokens_measured'])} |
| Output tokens | {show(summary['output_tokens_measured'])} |
| Token measurement coverage | {len(measured)} / {candidate['expected']} tasks |
| Model calls | {summary['model_calls_measured']} across {summary['call_measured_tasks']} measured tasks |
| Requests without complete usage | {show(summary['requests_without_complete_usage'])} |
| Available standardized model cost | ${show(summary['available_standardized_cost_usd'])} |
| Complete / available cost coverage | {len(costs)} / {len(available_costs)} of {candidate['expected']} tasks |
| Median full runner time, valid tasks | {show(summary['median_full_runner_seconds_all_valid'])} seconds |
| Median full runner time, successful tasks | {show(summary['median_full_runner_seconds_successes'])} seconds |

Costs use the frozen K3 rates with complete first-cold task totals taking precedence
over observed-call lower bounds, including failures. Missing data is not zero.
Tasks with incomplete usage retain unknown complete costs. Actual Kimi Coding billing and Runta
charges are not available. Runner time excludes restore and image pulls.

[Comparison chart and task evidence](report/index.html) · [Machine-readable summary](summary.json)

Provider, corpus and isolation equivalence to the published baselines has not
been established with a matched control. Source: https://frontierharness.org/
"""
(run / "SUMMARY.md").write_text(markdown)
print(json.dumps(summary, indent=2))
