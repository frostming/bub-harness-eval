#!/usr/bin/env bash
set -euo pipefail
suite=$1 task=$2 model=$3 jobs=$4
export PATH="$HOME/.local/bin:$PATH"
export PYTHONPATH=/work/agents
export BUB_ANTHROPIC_API_KEY=runta-secret-stub
case "$suite" in
  terminal-bench)
    exec harbor run -d terminal-bench@2.0 -i "$task" -a bub_harbor:BubAgent \
      -m "$model" --jobs-dir "$jobs" --extra-docker-compose /work/runta-ca-overlay.yaml -r 0 -n 1 -y ;;
  datacurve)
    docker image inspect fh-pier-egress-proxy:v1 >/dev/null 2>&1 || \
      docker load -i /work/fh-pier-egress-proxy.tar
    exec pier run -p "/work/deep-swe/tasks/$task" --agent-import-path bub_pier:BubAgent \
      --model "$model" --jobs-dir "$jobs" -r 0 -n 1 -y ;;
  *) echo "Unknown suite: $suite" >&2; exit 2 ;;
esac
