# Bub 0.3.1.dev1+geccbf7c84 on FrontierHarness Eval

![Pass rate versus median cost per task, Bub 0.3.1.dev1+geccbf7c84 against the FrontierHarness Eval baselines](chart.svg)

## Result

| Metric | Value |
| --- | --- |
| Pass rate | 63.3% |
| Tasks passed | 19 / 30 |
| Cost per pass | $2.64 |
| Complete cost coverage | 30/30 tasks |
| Median cost per successful task | $0.10 (19/19 successes measured) |
| Median time per successful task | 2m 3s |
| Median cache hit rate | 81.0% |
| Cache measurement coverage | 19/19 successful tasks with measured cache rates |
| Mean turns | 22.0 |

## Comparison · Provisional

| # | Harness | Pass rate | Median cost per task | Cache, median | Median time |
| --- | --- | --- | --- | --- | --- |
| 01 | Codex | 66.7% | $3.47 | 88.0% | 6m 43s |
| 02 | **Bub 0.3.1.dev1+geccbf7c84** | 63.3% | $2.64 | 81.0% | 2m 3s |
| 03 | Claude Code | 63.3% | $18.34 | 67.8% | 9m 38s |
| 04 | DSH Creator | 63.3% | $3.28 | 84.3% | 6m 44s |
| 05 | DSH PTC | 60.0% | $4.58 | 87.2% | 7m 44s |
| 06 | DSH Standard | 60.0% | $3.46 | 86.5% | 6m 17s |
| 07 | Pi | 60.0% | $2.43 | 79.4% | 7m 33s |
| 08 | DSH Minimal | 56.7% | $4.72 | 84.6% | 5m 41s |
| 09 | Kimi Code | 56.7% | $3.65 | 88.0% | 7m 56s |
| 10 | Oh My Pi | 56.7% | $4.75 | 82.2% | 6m 46s |
| 11 | Exo Harness | 53.3% | $1.05 | 70.3% | 6m 17s |
| 12 | Hermes | 50.0% | $2.90 | 85.9% | 6m 58s |
| 13 | OpenCode | 50.0% | $3.24 | 78.4% | 6m 27s |

## Reproducibility

| Field | Value |
| --- | --- |
| Run id | `2026-09-13-bub-main-eccbf7c` |
| Golden checkpoint | `fh-golden-bub-main-eccbf7c` |
| Model | `anthropic:k3` |
| Provider | `custom` |
| Harness repo | `https://github.com/bubbuild/bub` |
| Harness commit | `eccbf7c84bc88be282285d64a813c62ce0b53afb` |
| Runtime | 4 vCPU, 8192 MiB |
| Harbor | `0.22.0` |
| Pier | `0.3.1` |
| DeepSWE corpus | `435ee89ec2f2e2289f33b0da4f992f0b7b7266b9` |
| Started | 2026-09-13T15:17:58Z |


## Task results

| Task | Result | Cost | Time | Turns | Cache hit rate | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| `datacurve/anko-typed-variable-bindings` | failure | $1.23 | 23m 50s | 79 | 97.2% | [evidence](../trials/datacurve-anko-typed-variable-bindings) |
| `datacurve/arktype-json-schema-refs-dependencies` | failure | $8.21 | 90m 0s | 260 | 99.2% | [evidence](../trials/datacurve-arktype-json-schema-refs-dependencies) |
| `datacurve/expr-try-catch-errors` | failure | $9.41 | 90m 0s | 267 | 99.0% | [evidence](../trials/datacurve-expr-try-catch-errors) |
| `datacurve/fastapi-deprecation-response-headers` | failure | $1.01 | 18m 1s | 53 | 96.6% | [evidence](../trials/datacurve-fastapi-deprecation-response-headers) |
| `datacurve/httpx-multipart-response-parsing` | failure | $11.80 | 90m 0s | 334 | 99.3% | [evidence](../trials/datacurve-httpx-multipart-response-parsing) |
| `datacurve/katex-multicolumn-array-spans` | failure | $2.58 | 32m 56s | 126 | 98.4% | [evidence](../trials/datacurve-katex-multicolumn-array-spans) |
| `datacurve/meriyah-explicit-resource-declarations` | failure | $4.40 | 37m 40s | 172 | 98.0% | [evidence](../trials/datacurve-meriyah-explicit-resource-declarations) |
| `datacurve/python-statemachine-state-data-scoping` | pass | $5.78 | 62m 34s | 178 | 99.0% | [evidence](../trials/datacurve-python-statemachine-state-data-scoping) |
| `datacurve/scc-bounded-memory-spilling` | failure | $1.11 | 16m 58s | 58 | 96.8% | [evidence](../trials/datacurve-scc-bounded-memory-spilling) |
| `terminal-bench/build-cython-ext` | pass | $0.60 | 8m 31s | 55 | 96.3% | [evidence](../trials/terminal-bench-build-cython-ext) |
| `terminal-bench/chess-best-move` | pass | $0.15 | 3m 3s | 14 | 86.9% | [evidence](../trials/terminal-bench-chess-best-move) |
| `terminal-bench/code-from-image` | pass | $0.83 | 17m 51s | 50 | 95.8% | [evidence](../trials/terminal-bench-code-from-image) |
| `terminal-bench/constraints-scheduling` | pass | $0.08 | 1m 55s | 4 | 69.1% | [evidence](../trials/terminal-bench-constraints-scheduling) |
| `terminal-bench/db-wal-recovery` | failure | $0.58 | 11m 28s | 54 | 95.5% | [evidence](../trials/terminal-bench-db-wal-recovery) |
| `terminal-bench/dna-insert` | pass | $0.19 | 3m 35s | 15 | 89.2% | [evidence](../trials/terminal-bench-dna-insert) |
| `terminal-bench/extract-elf` | pass | $0.10 | 3m 2s | 8 | 81.0% | [evidence](../trials/terminal-bench-extract-elf) |
| `terminal-bench/gcode-to-text` | failure | $0.89 | 15m 32s | 49 | 95.4% | [evidence](../trials/terminal-bench-gcode-to-text) |
| `terminal-bench/git-leak-recovery` | pass | $0.06 | 2m 1s | 4 | 64.4% | [evidence](../trials/terminal-bench-git-leak-recovery) |
| `terminal-bench/kv-store-grpc` | ★ Solved · 0/12 baselines passed | $0.04 | **1m 38s** | 7 | 80.8% | [evidence](../trials/terminal-bench-kv-store-grpc) |
| `terminal-bench/largest-eigenval` | ★ Solved · 0/12 baselines passed | $0.19 | **4m 56s** | 15 | 88.6% | [evidence](../trials/terminal-bench-largest-eigenval) |
| `terminal-bench/log-summary-date-ranges` | pass | $0.04 | 1m 29s | 4 | 67.4% | [evidence](../trials/terminal-bench-log-summary-date-ranges) |
| `terminal-bench/merge-diff-arc-agi-task` | pass | $0.11 | 2m 57s | 18 | 90.4% | [evidence](../trials/terminal-bench-merge-diff-arc-agi-task) |
| `terminal-bench/modernize-scientific-stack` | pass | $0.04 | 1m 27s | 4 | 68.9% | [evidence](../trials/terminal-bench-modernize-scientific-stack) |
| `terminal-bench/multi-source-data-merger` | pass | $0.06 | 1m 37s | 5 | 73.4% | [evidence](../trials/terminal-bench-multi-source-data-merger) |
| `terminal-bench/openssl-selfsigned-cert` | pass | $0.05 | 1m 29s | 6 | 77.7% | [evidence](../trials/terminal-bench-openssl-selfsigned-cert) |
| `terminal-bench/polyglot-c-py` | failure | $0.21 | 6m 22s | 8 | 78.2% | [evidence](../trials/terminal-bench-polyglot-c-py) |
| `terminal-bench/regex-log` | pass | $0.12 | 3m 47s | 6 | 75.8% | [evidence](../trials/terminal-bench-regex-log) |
| `terminal-bench/sanitize-git-repo` | pass | $0.12 | 2m 0s | 10 | 82.9% | [evidence](../trials/terminal-bench-sanitize-git-repo) |
| `terminal-bench/sqlite-db-truncate` | pass | $0.10 | 2m 3s | 9 | 83.5% | [evidence](../trials/terminal-bench-sqlite-db-truncate) |
| `terminal-bench/vulnerable-secret` | pass | $0.07 | 1m 7s | 6 | 73.3% | [evidence](../trials/terminal-bench-vulnerable-secret) |


---

Baseline data and methodology: [FrontierHarness Eval](https://frontierharness.org/)
