#!/usr/bin/env bash
# Build the site and add the result as a new commit on the `site` branch
# (what Hostinger serves). History is kept linear so the server can fast-forward.
set -euo pipefail
cd "$(dirname "$0")"
REPO=$(pwd)
python3 build.py
SRC_SHA=$(git rev-parse --short HEAD)
REMOTE=$(git remote get-url origin)
TMP=$(mktemp -d)
if git ls-remote --exit-code --heads "$REMOTE" site >/dev/null 2>&1; then
  git clone -q --depth 1 --branch site "$REMOTE" "$TMP"
else
  git init -q -b site "$TMP"
fi
find "$TMP" -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
cp -a "$REPO/dist/." "$TMP/"
cd "$TMP"
git add -A
if git diff --cached --quiet; then
  echo "No changes to publish"; exit 0
fi
git -c user.name="Scandinavian Nomads bot" -c user.email="connect@scandinaviannomads.com" commit -qm "Build from main@$SRC_SHA"
git -c push.negotiate=true push -q "$REMOTE" HEAD:site
echo "Published build of main@$SRC_SHA to branch 'site'"
