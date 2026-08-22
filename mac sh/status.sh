#!/usr/bin/env bash
# PRJs runner | platform: mac | scope: repo-local
set -euo pipefail
cd "$(cd "$(dirname "$0")/.." && pwd)"
git status -sb
git log -3 --oneline
