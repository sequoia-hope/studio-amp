#!/usr/bin/env bash
# launch.sh — start (or reattach to) this project's agent session.
#   ./launch.sh [-r] [agent]     -r restarts it; agent defaults to the first offered
set -euo pipefail
PROJ="$(command -v proj || echo "/home/sequoia/Software/overseer/core/proj")"
exec "$PROJ" agent studio-amp "$@"
