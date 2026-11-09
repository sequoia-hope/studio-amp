#!/usr/bin/env bash
# launch.sh — start (or reattach to) this project's agent session.
#   ./launch.sh [-r] [agent]     -r restarts it; agent defaults to the first offered
set -euo pipefail
PROJ="$(command -v proj)" || { echo "launch.sh: proj not found on PATH" >&2; exit 1; }
exec "$PROJ" agent studio-amp "$@"
