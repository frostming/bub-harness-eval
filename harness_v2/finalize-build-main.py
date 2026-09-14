"""Finalize a Bub-main build while enforcing the prior dependency baseline."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


BASELINE_SHA256 = {
    "/work/agents/bub_common.py": "6a3678cad49fcef3d9575fa82d768f481fd54e9e95a6d17c29945bd8bdfdaa0a",
    "/work/agents/bub_instrument.py": "87d88bcb57935b77550f4a67c10550fce79d3fde2281f3bf053a402d25bb2d28",
    "/work/agents/bub_pier.py": "c37904288ffafbdb4cdcd898fdfa1489ee77583e2a14a5fb83d17151d9acd75f",
    "/work/agents/bub_harbor.py": "e1aa2c5b3d70b7679934dff8aee7da4c0abec7f80a255863e3f81feec4d03a57",
    "/work/agents/run-task.sh": "105880ca99755b9a64bac1907b3c622a95a2b88898097841888e07f21df8b171",
    "/work/bub-freeze.txt": "2abf9f4848aa5ae196b5d564dd1403bbe57de213161029fbf66c27e36158a768",
    "/work/fh-pier-egress-proxy.tar": "22439417330e6e896fcd1ca68026466cd569244f9a9a6f9c493767c4b2fca0d1",
    "/tmp/data-gym-cache/fb374d419588a4632f3f557e76b4b70aebbca790": "446a9538cb6c348e3516120d7c08b09f57c36495e2acfffe59a5bf8b0cfb1a2d",
}


def digest(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", "/work/harness", *args], text=True
    ).strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--base-checkpoint", required=True)
    args = parser.parse_args()

    actual = {path: digest(path) for path in BASELINE_SHA256}
    mismatches = {
        path: {"expected": BASELINE_SHA256[path], "actual": value}
        for path, value in actual.items()
        if value != BASELINE_SHA256[path]
    }
    if mismatches:
        raise SystemExit(f"baseline files changed: {json.dumps(mismatches, indent=2)}")

    candidate_freeze = Path("/work/bub-freeze-main.txt")
    baseline_freeze = Path("/work/bub-freeze.txt")
    if candidate_freeze.read_bytes() != baseline_freeze.read_bytes():
        raise SystemExit("installed dependency freeze differs from baseline")

    manifest_path = Path("/work/manifest.json")
    manifest = json.loads(manifest_path.read_text())
    manifest.update(
        checkpoint=args.checkpoint,
        base_checkpoint=args.base_checkpoint,
        harness_ref="refs/heads/main",
        harness_commit=git("rev-parse", "HEAD"),
        harness_describe=git("describe", "--tags", "--always"),
        harness_installed_version=importlib.metadata.version("bub"),
        created_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
            "+00:00", "Z"
        ),
        dependency_baseline_checkpoint=args.base_checkpoint,
        dependency_lock_unchanged_from_base=True,
        dependency_freeze_sha256=actual["/work/bub-freeze.txt"],
        adapter_revision="bub-v4-portable-usage-offline-proxy-tokenizer",
        credential_handling="literal runta-secret-stub; per-runtime x-api-key egress injection",
        pier_proxy_preparation="Original Pier Squid Dockerfile prebuilt; offline archive loaded per restore; same provider-only ACL and internal network",
        preflight="synthetic Harbor and Pier file/shell probes passed; no formal tasks executed in build",
        adapter_and_dependency_sha256=actual,
        portable_bundle_sha256=digest("/work/bub-portable.tar.gz"),
    )
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
