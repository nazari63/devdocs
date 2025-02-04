#!/usr/bin/env bash

set -euo pipefail

COMMIT=${COMMIT:-"true"}
SUBMODULES=$(git submodule status | awk '{print $2}' | cut -d'/' -f2)

for SUBMODULE in $SUBMODULES; do
  echo "Updating $SUBMODULE"
  cd "submodules/$SUBMODULE"
  git fetch
  git reset --hard
  if [[ "$SUBMODULE" == "optimism" ]]; then
    git checkout develop
    git pull origin develop
  else
    git checkout main
    git pull origin main
  fi

  git add .
  cd ../..
done

if [ "$COMMIT" == "true" ]; then
  if git diff --cached --quiet; then
    echo "No changes to commit"
  else
    git add submodules
    git commit -m "Update submodules"
  fi
fi