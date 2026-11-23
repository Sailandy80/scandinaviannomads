#!/usr/bin/env bash
# Build the site and push the result to the `site` branch (what Hostinger serves).
set -euo pipefail
cd "$(dirname "$0")"
python3 build.py
SRC_SHA=$(git rev-parse --short HEAD)
TMP=$(mktemp -d)
cp -a dist/. "$TMP"/
cd "$TMP"
git init -q -b site
git add -A
git -c user.name="Scandinavian Nomads bot" -c user.email="connect@scandinaviannomads.com" commit -qm "Build from main@$SRC_SHA"
REMOTE=$(git -C "$OLDPWD" remote get-url origin)
git push -f "$REMOTE" site:site
echo "Published build of main@$SRC_SHA to branch 'site'"
