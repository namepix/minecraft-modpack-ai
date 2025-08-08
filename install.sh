#!/bin/bash
# Wrapper: fully automated installation for ModpackAI (NeoForge mod)
# Delegates to install_mod.sh to keep docs simple.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ ! -x "${SCRIPT_DIR}/install_mod.sh" ]]; then
  chmod +x "${SCRIPT_DIR}/install_mod.sh" || true
fi

echo "🚀 Running ModpackAI full install..."
"${SCRIPT_DIR}/install_mod.sh" "$@"
echo "✅ Done."

