# Bub FrontierHarness Eval — final handoff

This workspace retains only the final latest-main evaluation and the code needed
to inspect or reproduce it.

## Canonical evaluation

- Run: `frontierharness-eval/runs/2026-09-13-bub-main-eccbf7c`
- Harness: `https://github.com/bubbuild/bub`
- Commit: `eccbf7c84bc88be282285d64a813c62ce0b53afb`
- Display label: `Bub 0.3.1.dev1+geccbf7c84`
- Golden checkpoint: `fh-golden-bub-main-eccbf7c`
- Base dependency checkpoint: `fh-golden-bub-clean-v4`
- Model/provider route: `anthropic:k3` through the custom Kimi endpoint
- Runtime per task: 4 vCPU, 8192 MiB RAM, 50 GiB disk
- Concurrency: at most three workers
- Task timeout: 5400 seconds

The checkpoint was derived from the validated clean-v4 dependency baseline.
Only Bub was reinstalled from the pinned main commit with `--no-deps`; adapters,
dependency freeze, proxy setup, tokenizer cache, Harbor, Pier, and DeepSWE corpus
were unchanged. Trial manifests in the canonical run are the authoritative record.

## Final result

- 30/30 valid tasks; 0 infrastructure-invalid; 0 missing
- 19 successes and 11 failures; 63.3% pass rate
- 119,707,944 measured input tokens
- 657,768 measured output tokens
- 1,878 model calls, all with complete usage
- $50.1494688 standardized first-cold cost at the frozen benchmark rates
- $2.64 website-aligned cost per pass
- Observed provisional position: #2

The candidate remains `comparable: false`: provider, corpus, and isolation
equivalence to the published baselines has not been established with a matched
control. The provisional display does not change that status.

## Final artifacts

- `candidate.json` — normalized candidate metrics
- `summary.json` and `SUMMARY.md` — machine/human run summary
- `audit.json` and `observed-cost-audit.json` — evidence and usage audit
- `report/index.html` — self-contained report
- `report/REPORT.md` — Markdown report
- `report/chart.svg` — comparison scatter plot
- `trials/` — all 30 canonical trial records and evidence archives

The report and SVG were visually verified at desktop and 390px viewport widths.
Bub is marked by a large orange five-point star with an outline halo. Tables and
the wide chart scroll horizontally on narrow screens.

## Audit notes

Three 5400-second DeepSWE timeout failures (ArkType, Expr, and HTTPX) lack the
final `model.patch` artifact and have trial-total/per-call differences. Their
request-level usage is nevertheless complete and their timeout began after agent
execution, so they are valid failures. G-code is also a valid agent-timeout
failure with complete usage. All 30 retained `evidence.tar.gz` files pass gzip
integrity checks.

## Retained code

- `harness_v2/finalize-build-main.py` validates that the main checkpoint differs
  from the base only in the pinned Bub installation.
- `harness_v2/resume-main-eval.sh` is the quota-aware three-shard supervisor.
- `harness_v2/run-task.sh` and `harness_v2/bub_*.py` are the exact retained
  adapters used by the checkpoint.
- `harness_v2/eval-scripts/` contains the trial, transport, normalization, chart,
  and report implementation used for this run.
- `harness_v2/audit_results.py` and `harness_v2/summarize.py` generate the final
  audit and summary.

The adapter source intentionally retains the clean-v4 adapter identity because
it was held byte-for-byte constant. The evaluated Bub version is recorded in each
trial manifest and in the report, not inferred from those adapter strings.

## Regenerating normalized output

From `frontierharness-eval/`:

```bash
node ../harness_v2/eval-scripts/normalize-results.mjs \
  --run runs/2026-09-13-bub-main-eccbf7c \
  --label "Bub 0.3.1.dev1+geccbf7c84"

../.venv/bin/python ../harness_v2/audit_results.py \
  runs/2026-09-13-bub-main-eccbf7c

node ../harness_v2/eval-scripts/generate-chart.mjs \
  --run runs/2026-09-13-bub-main-eccbf7c --display-rank true

node ../harness_v2/eval-scripts/build-report.mjs \
  --run runs/2026-09-13-bub-main-eccbf7c --display-rank true

../.venv/bin/python ../harness_v2/summarize.py \
  runs/2026-09-13-bub-main-eccbf7c
```

Do not retry or replace any valid canonical task. Use a new run ID for a new
experiment.
