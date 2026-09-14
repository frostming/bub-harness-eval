"""Audit collected evidence without mutating canonical trial outcomes."""
import hashlib
import json
import sys
from pathlib import Path

run = Path(sys.argv[1]).resolve()
expected = json.loads((run / "run.json").read_text())
pricing = json.loads((Path(__file__).parent / "eval-scripts" / "pricing.json").read_text())
rates = pricing["models"]["k3"]
observed_tasks = []
rows = []
for path in sorted((run / "trials").glob("*/trial.json")):
    trial = json.loads(path.read_text())
    if trial.get("recovery"):
        continue
    row = {"id": trial["id"], "status": trial["status"], "checks": [], "warnings": []}
    results = sorted((path.parent / "jobs").rglob("result.json"))
    leaves = [p for p in results if not any(p.parent in q.parents for q in results if p != q)]
    if len(leaves) != 1:
        row["warnings"].append(f"Expected one leaf result; found {len(leaves)}")
        rows.append(row)
        continue
    leaf = leaves[0]
    result = json.loads(leaf.read_text())
    row["rewards"] = (result.get("verifier_result") or {}).get("rewards")
    row["exception_type"] = (result.get("exception_info") or {}).get("exception_type")
    row["result_path"] = str(leaf.relative_to(run))
    manifest = json.loads((path.parent / "manifest.json").read_text())
    if manifest.get("checkpoint") == expected.get("checkpoint"):
        row["checks"].append("checkpoint matches run")
    else:
        row["warnings"].append("checkpoint differs from run")
    archive = path.parent / "evidence.tar.gz"
    if archive.is_file():
        with archive.open("rb") as stream:
            row["local_evidence_sha256"] = hashlib.file_digest(stream, "sha256").hexdigest()
        row["checks"].append("retained evidence archive")
    usage_paths = sorted((leaf.parent / "agent").rglob("bub-usage.jsonl"))
    events = []
    for usage_path in usage_paths:
        for line in usage_path.read_text().splitlines():
            if line.strip():
                events.append(json.loads(line))
    requests = {e.get("call_id") for e in events if e.get("event") == "request"}
    usages_by_id = {}
    for event in events:
        if event.get("event") != "usage" or not event.get("call_id"):
            continue
        previous = usages_by_id.get(event["call_id"])
        if previous and previous["usage"] != event["usage"]:
            raise ValueError(f"Conflicting usage for {trial['id']} call {event['call_id']}")
        usages_by_id[event["call_id"]] = event
    usages = list(usages_by_id.values())
    complete = bool(requests) and requests == {e.get("call_id") for e in usages}
    row["observed_requests"] = len(requests)
    row["observed_complete_calls"] = len(usages)
    row["complete_usage_coverage"] = complete
    if complete:
        inp = sum(sum(e["usage"].get(k, 0) or 0 for k in
                      ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
                  for e in usages)
        out = sum(e["usage"].get("output_tokens", 0) or 0 for e in usages)
        if (inp, out, len(usages)) == (trial.get("input_tokens"), trial.get("output_tokens"), trial.get("turns")):
            row["checks"].append("per-call usage matches trial totals")
        else:
            row["warnings"].append("per-call usage and trial totals differ")
    else:
        row["warnings"].append("usage incomplete or absent; do not treat missing tokens as zero")
    # Preserve measured-call lower bounds separately from canonical complete costs.
    # Pending trials and archived attempts are deliberately excluded above.
    token_keys = ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens", "output_tokens")
    measured = [e for e in usages if all(
        isinstance(e["usage"].get(k), int) and e["usage"][k] >= 0 for k in token_keys)]
    totals = {k: sum(e["usage"][k] for e in measured) for k in token_keys}
    measured_ids = {e["call_id"] for e in measured}
    total_input = sum(totals[k] for k in token_keys[:3])
    observed_tasks.append({
        "task": trial["id"], "status": trial["status"],
        "requests": len(requests), "usage_calls": len(measured),
        "missing_usage": len(requests - measured_ids),
        "observed_input_tokens": total_input if measured else None,
        "observed_cached_input_tokens": totals["cache_read_input_tokens"] if measured else None,
        "observed_output_tokens": totals["output_tokens"] if measured else None,
        "observed_raw_cache_rate": totals["cache_read_input_tokens"] / total_input if total_input else None,
        "observed_cost_usd": (
            totals["input_tokens"] * rates["fresh_input"]
            + totals["cache_read_input_tokens"] * rates["cache_read"]
            + totals["cache_creation_input_tokens"] * rates["cache_write"]
            + totals["output_tokens"] * rates["output"]
        ) / pricing["unit_tokens"] if measured else None,
        "usage_complete": bool(requests) and requests == measured_ids,
        "evidence": [str(p.relative_to(run)) for p in usage_paths],
    })
    artifact_manifest = leaf.parent / "artifacts" / "manifest.json"
    if artifact_manifest.is_file():
        failed = [a.get("source") for a in json.loads(artifact_manifest.read_text())
                  if a.get("status") == "failed"]
        if failed:
            row["warnings"].append("Artifacts unavailable: " + ", ".join(failed))
    ctrf = leaf.parent / "verifier" / "ctrf.json"
    if ctrf.is_file():
        tests = json.loads(ctrf.read_text()).get("results", {}).get("tests", [])
        row["failed_test_names"] = [t.get("name") for t in tests if t.get("status") == "failed"]
        row["checks"].append("retained verifier test report")
    rows.append(row)

audit = {"run_id": run.name, "collected_tasks": len(rows), "tasks": rows}
(run / "audit.json").write_text(json.dumps(audit, indent=2) + "\n")
observed_costs = [t["observed_cost_usd"] for t in observed_tasks if t["observed_cost_usd"] is not None]
observed = {
    "run_id": run.name, "pricing": pricing["version"],
    "requests": sum(t["requests"] for t in observed_tasks),
    "usage_calls": sum(t["usage_calls"] for t in observed_tasks),
    "missing_usage": sum(t["missing_usage"] for t in observed_tasks),
    "observed_cost_usd": sum(observed_costs) if observed_costs else None,
    "basis": "Observed complete-call tokens only, no first-call cold adjustment; not actual billing. Canonical complete task costs take precedence in reports. Pending trials and archived attempts excluded.",
    "tasks": observed_tasks,
}
(run / "observed-cost-audit.json").write_text(json.dumps(observed, indent=2) + "\n")
print(json.dumps({"collected_tasks": len(rows), "tasks_with_warnings": [
    {"id": row["id"], "warnings": row["warnings"]} for row in rows if row["warnings"]
]}, indent=2))
