"""Portable installation, invocation and evidence shared by both runner adapters."""
import asyncio
import json
import shlex
from pathlib import Path

ROOT = Path(__file__).parent
LOGS = "/logs/agent"


async def setup(environment):
    await environment.upload_file("/work/bub-portable.tar.gz", "/tmp/fh-bub.tar.gz")
    result = await environment.exec(
        command="tar -xzf /tmp/fh-bub.tar.gz -C / && mkdir -p /logs/agent && "
                "/root/.bub/.venv/bin/bub --help >/dev/null", user="root", timeout_sec=600)
    if result.return_code:
        raise RuntimeError(f"Bub installation failed: {result.stderr}")
    await environment.upload_file(ROOT / "bub_instrument.py", "/tmp/fh-bub-instrument.py")
    await environment.upload_dir("/tmp/data-gym-cache", "/opt/fh-tiktoken")
    await environment.upload_file("/etc/ssl/certs/ca-certificates.crt", "/tmp/fh-ca-bundle.crt")


def read_usage(path):
    events = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    requests = {e["call_id"] for e in events if e.get("event") == "request"}
    usages = [e for e in events if e.get("event") == "usage"]
    complete = bool(requests) and requests == {e.get("call_id") for e in usages}
    return usages, complete


async def collect(environment, logs_dir, context):
    logs_dir.mkdir(parents=True, exist_ok=True)
    await environment.download_dir(LOGS, logs_dir)
    paths = list(logs_dir.rglob("bub-usage.jsonl"))
    if not paths:
        return
    usages, complete = read_usage(paths[0])
    context.metadata = {"usage_complete": complete, "measured_calls": len(usages)}
    if not usages or not complete:
        return
    context.n_input_tokens = sum(sum(e["usage"].get(k, 0) or 0 for k in
        ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")) for e in usages)
    context.n_cache_tokens = sum(e["usage"].get("cache_read_input_tokens", 0) or 0 for e in usages)
    context.n_output_tokens = sum(e["usage"].get("output_tokens", 0) or 0 for e in usages)


async def run(agent, instruction, environment, context):
    env = {
        "BUB_MODEL": agent.model_name or "anthropic:k3",
        "BUB_ANTHROPIC_API_BASE": "https://api.kimi.com/coding/",
        "BUB_ANTHROPIC_API_KEY": "runta-secret-stub",
        "BUB_HOME": "/logs/agent/bub-home",
        "FH_USAGE_PATH": "/logs/agent/bub-usage.jsonl",
        "NO_COLOR": "1",
        "TIKTOKEN_CACHE_DIR": "/opt/fh-tiktoken",
        "SSL_CERT_FILE": "/tmp/fh-ca-bundle.crt",
        "REQUESTS_CA_BUNDLE": "/tmp/fh-ca-bundle.crt",
    }
    # Pier exposes provider-only proxy variables separately from environment.exec.
    # Custom BaseAgent adapters must apply them just like BaseInstalledAgent does.
    if hasattr(environment, "agent_process_env"):
        env = environment.agent_process_env(env)
    command = (
        "/root/.bub/.venv/bin/python /tmp/fh-bub-instrument.py run "
        + shlex.quote(instruction) + " > /logs/agent/bub-output.txt 2>&1"
    )
    try:
        result = await environment.exec(command=command, env=env)
        if result.return_code:
            raise RuntimeError(f"Bub exited with status {result.return_code}; see bub-output.txt")
    finally:
        await asyncio.shield(collect(environment, agent.logs_dir, context))
