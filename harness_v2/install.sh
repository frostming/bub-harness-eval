#!/usr/bin/env bash
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
export UV_PYTHON_INSTALL_DIR=/opt/fh-python
export UV_MANAGED_PYTHON=1
uv python install 3.12
curl -fsSL https://bub.build/install.sh -o /work/bub-standalone-install.sh
bash /work/bub-standalone-install.sh --preset recommended
# Retain the requested preset, then pin the core harness to the evaluated checkout.
uv pip install --python /root/.bub/.venv/bin/python --no-deps /work/harness
uv pip freeze --python /root/.bub/.venv/bin/python > /work/bub-freeze.txt
mkdir -p /work/agents
tar -czf /work/bub-portable.tar.gz -C / opt/fh-python root/.bub/.venv
sha256sum /work/bub-portable.tar.gz > /work/bub-portable.sha256
# The controller uploads adapters and checks the build before releasing this gate.
while ! test -f /work/fh-adapters-ready; do sleep 5; done
/root/.local/share/uv/tools/harbor/bin/python -m compileall -q /work/agents
