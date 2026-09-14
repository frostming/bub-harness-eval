# Bounded retries for idempotent transport operations only. Never wrap a foreground
# harness command in retry: a disconnect does not mean the harness stopped.
retry_transport() {
  local attempt
  for ((attempt = 1; attempt <= ${FH_TRANSPORT_ATTEMPTS:-3}; attempt++)); do
    if "$@"; then return 0; fi
    if [ "$attempt" -lt "${FH_TRANSPORT_ATTEMPTS:-3}" ]; then
      sleep "${FH_RETRY_DELAY:-2}"
    fi
  done
  return 1
}

shell_quote() {
  local escaped_quote="'\\''"
  printf "'%s'" "${1//\'/$escaped_quote}"
}

# runta cp can return an error even after delivering the entire file. A checksum
# distinguishes that case from an incomplete transfer; each retry has a fresh target.
file_sha256() {
  if command -v sha256sum >/dev/null; then
    sha256sum "$1" | awk '{print $1}'
  else
    shasum -a 256 "$1" | awk '{print $1}'
  fi
}

# Some Runta versions intermittently fail to download a regular remote file with
# "tar archive contained no regular file entry" even though the file is readable.
# Fall back to small, newline-terminated base64 chunks and still require the same
# end-to-end checksum before accepting the artifact. 3072 is divisible by three,
# so concatenating independently encoded full chunks introduces no interior padding.
copy_remote_base64_chunks() {
  local source=$1 target=$2 expected=$3 runtime remote_path size chunks chunk encoded actual
  case "$source" in
    *:*) runtime=${source%%:*}; remote_path=${source#*:} ;;
    *) return 1 ;;
  esac
  size=$(runta exec "$runtime" -- sh -lc \
    "stat -c %s $(shell_quote "$remote_path")" 2>/dev/null | tr -d '\r\n') || return 1
  case "$size" in ''|*[!0-9]*) return 1 ;; esac
  chunks=$(( (size + 3071) / 3072 ))
  rm -f "$target.b64.part" "$target.chunked.part"
  for ((chunk = 0; chunk < chunks; chunk++)); do
    encoded=$(runta exec "$runtime" -- sh -lc \
      "dd if=$(shell_quote "$remote_path") bs=3072 skip=$chunk count=1 2>/dev/null | base64 -w 0; printf '\n'" \
      2>/dev/null | tr -d '\r\n') || return 1
    case "$encoded" in ''|*[!A-Za-z0-9+/=]*) return 1 ;; esac
    printf '%s' "$encoded" >> "$target.b64.part"
  done
  python3 -c 'import base64, pathlib, sys; pathlib.Path(sys.argv[2]).write_bytes(base64.b64decode(pathlib.Path(sys.argv[1]).read_bytes(), validate=True))' \
    "$target.b64.part" "$target.chunked.part" || return 1
  actual=$(file_sha256 "$target.chunked.part" 2>/dev/null) || actual=""
  if [ -n "$actual" ] && [ "$actual" = "$expected" ]; then
    mv "$target.chunked.part" "$target"
    rm -f "$target.b64.part"
    return 0
  fi
  rm -f "$target.b64.part" "$target.chunked.part"
  return 1
}

copy_verified() {
  local source=$1 target=$2 expected=$3 attempt actual
  # Reuse evidence recovered through an alternate transport only when its full
  # checksum matches the freshly read remote archive hash.
  actual=$(file_sha256 "$target" 2>/dev/null) || actual=""
  if [ -n "$actual" ] && [ "$actual" = "$expected" ]; then
    return 0
  fi
  for ((attempt = 1; attempt <= ${FH_TRANSPORT_ATTEMPTS:-3}; attempt++)); do
    rm -f "$target.part"
    runta cp "$source" "$target.part" || true
    actual=$(file_sha256 "$target.part" 2>/dev/null) || actual=""
    if [ "$actual" = "$expected" ] && [ -n "$actual" ]; then
      mv "$target.part" "$target"
      return 0
    fi
    if [ "$attempt" -lt "${FH_TRANSPORT_ATTEMPTS:-3}" ]; then
      sleep "${FH_RETRY_DELAY:-2}"
    fi
  done
  rm -f "$target.part"
  copy_remote_base64_chunks "$source" "$target" "$expected"
}

wait_for_checkpoint() {
  local name=$1 timeout=$2 started state
  started=$(date +%s)
  while :; do
    state=$(runta checkpoint ls --json | jq -r --arg name "$name" \
      '.checkpoints[] | select(.display_name == $name) | .state') || state=""
    case "$state" in
      ready) return 0 ;;
      error|failed) echo "checkpoint $name entered $state" >&2; return 1 ;;
    esac
    if [ "$(( $(date +%s) - started ))" -ge "$timeout" ]; then
      echo "checkpoint $name did not become ready within ${timeout}s (state: ${state:-unknown})" >&2
      return 1
    fi
    sleep "${FH_POLL_INTERVAL:-5}"
  done
}
