# Bub FrontierHarness evaluation

Final evaluation of Bub at commit
`eccbf7c84bc88be282285d64a813c62ce0b53afb` against the 30-task
FrontierHarness Eval set.

- 30/30 valid tasks
- 19 passes, 11 failures
- 63.3% pass rate
- Observed provisional position: #2
- Standardized first-cold model cost: $50.1494688

[Open the self-contained report](frontierharness-eval/runs/2026-09-13-bub-main-eccbf7c/report/index.html)
or read the [Markdown report](frontierharness-eval/runs/2026-09-13-bub-main-eccbf7c/report/REPORT.md).

## Repository scope

This is an independent result repository. It intentionally does **not** vendor
the `frontier-harness-eval/eval` Git repository, any nested `.git`
directory, a Python virtual environment, or expanded copies of evidence already
stored in each trial's verified `evidence.tar.gz`.

The retained `harness_v2/` directory contains the adapters, supervisor,
accounting, audit, chart, and report code used for this run. The retained
`frontierharness-eval/runs/2026-09-13-bub-main-eccbf7c/` directory contains
the canonical result and all 30 evidence archives.

To regenerate reports, clone
[FrontierHarness Eval](https://github.com/frontier-harness-eval/eval) at commit
`e837a70`, copy this repository's canonical run into its `runs/` directory,
and use the commands in [EVALUATION-HANDOFF.md](EVALUATION-HANDOFF.md).

The candidate remains non-comparable to the published leaderboard because no
matched control established provider, corpus, and isolation equivalence. The
displayed #2 position is provisional.
