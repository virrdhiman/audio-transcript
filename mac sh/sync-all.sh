#!/usr/bin/env bash
# PRJs runner | platform: mac | scope: repo-local
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
git status -sb
read -r -p "Commit? [Y/n] " c || true
if [[ "${c:-Y}" != [Nn] ]]; then
  git add -A
  git reset HEAD -- .env .env.* 2>/dev/null || true
  git reset HEAD -- scripts/strip-* 2>/dev/null || true
  read -r -p "Message: " m
  [ -n "${m:-}" ] && git commit -m "$m" || true
fi
read -r -p "Push? [Y/n] " p || true
if [[ "${p:-Y}" != [Nn] ]]; then git push origin HEAD; fi
