#!/usr/bin/env bash
# Persistent quota-aware supervisor for the Bub latest-main FrontierHarness run.
set -uo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
RUN_ID=2026-09-13-bub-main-eccbf7c
CHECKPOINT=fh-golden-bub-main-eccbf7c
RUN_DIR="$ROOT/frontierharness-eval/runs/$RUN_ID"
CONTROLLER="$RUN_DIR/controller"
SCRIPTS="$ROOT/harness_v2/eval-scripts"
SHARD_ROOT=/tmp/fh-bub-main-eccbf7c-shards
LABEL='Bub 0.3.1.dev1+geccbf7c84'
mkdir -p "$CONTROLLER" "$SHARD_ROOT/1" "$SHARD_ROOT/2" "$SHARD_ROOT/3"
printf '%s\n' "$$" > "$CONTROLLER/supervisor.pid"
trap 'rm -f "$CONTROLLER/supervisor.pid"' EXIT

log() {
  printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" \
    | tee -a "$CONTROLLER/supervisor.log"
}

ensure_shards() {
  local i=0 toml task_dir shard count
  for toml in "$ROOT"/frontierharness-eval/tasks/*/task.toml; do
    task_dir=${toml%/task.toml}
    shard=$((i % 3 + 1))
    if [ ! -e "$SHARD_ROOT/$shard/${task_dir##*/}" ]; then
      ln -s "$task_dir" "$SHARD_ROOT/$shard/${task_dir##*/}"
    fi
    i=$((i + 1))
  done
  for shard in 1 2 3; do
    count=$(find -L "$SHARD_ROOT/$shard" -mindepth 2 -maxdepth 2 -name task.toml | wc -l | tr -d ' ')
    if [ "$count" != 10 ]; then
      log "invalid shard $shard task count: $count"
      return 1
    fi
  done
}

valid_count() {
  find "$RUN_DIR/trials" -name trial.json -exec jq -r \
    'select(.status == "success" or .status == "failure") | 1' {} + 2>/dev/null | wc -l | tr -d ' '
}

wait_for_quota() {
  local state rc
  while :; do
    state=$("$ROOT/.venv/bin/python" "$ROOT/harness_v2/check-kimi-quota.py" 2>&1)
    rc=$?
    log "quota $state"
    [ "$rc" -eq 0 ] && return 0
    sleep 300
  done
}

run_shards() {
  local shard rc=0
  local common=(
    --checkpoint "$CHECKPOINT" --harness bub --run-id "$RUN_ID"
    --provider custom --model anthropic:k3 --out "$ROOT/frontierharness-eval/runs"
    --cmd 'bash /work/agents/run-task.sh {suite} {task} {model} {jobs}'
    --timeout 5400 --secret-name BUB_ANTHROPIC_API_KEY --secret-host api.kimi.com
  )
  local pids=()
  for shard in 1 2 3; do
    bash "$SCRIPTS/run-trials.sh" "${common[@]}" --tasks "$SHARD_ROOT/$shard" \
      >> "$CONTROLLER/shard-$shard.log" 2>&1 &
    pids+=("$!")
  done
  for shard in 0 1 2; do
    wait "${pids[$shard]}" || rc=1
  done
  return "$rc"
}

finalize() {
  cd "$ROOT/frontierharness-eval" || return 1
  node "$SCRIPTS/normalize-results.mjs" --run "runs/$RUN_ID" --label "$LABEL" || return 1
  "$ROOT/.venv/bin/python" "$ROOT/harness_v2/audit_results.py" "runs/$RUN_ID" || return 1
  node "$SCRIPTS/generate-chart.mjs" --run "runs/$RUN_ID" --display-rank true || return 1
  node "$SCRIPTS/build-report.mjs" --run "runs/$RUN_ID" --display-rank true || return 1
  "$ROOT/.venv/bin/python" "$ROOT/harness_v2/summarize.py" "runs/$RUN_ID" || return 1
  log "complete: report=$RUN_DIR/report/index.html"
}

ensure_shards || exit 1
log "supervisor started; valid=$(valid_count)/30"
while [ "$(valid_count)" -lt 30 ]; do
  if [ -f "$CONTROLLER/provider-blocked.json" ]; then
    wait_for_quota
    mv "$CONTROLLER/provider-blocked.json" \
      "$CONTROLLER/provider-blocked-before-resume-$(date -u +%Y%m%dT%H%M%SZ).json"
  fi
  log "launching three shards; valid=$(valid_count)/30"
  run_shards || true
  log "shards exited; valid=$(valid_count)/30"
  if [ ! -f "$CONTROLLER/provider-blocked.json" ] && [ "$(valid_count)" -lt 30 ]; then
    sleep 60
  fi
done
finalize
