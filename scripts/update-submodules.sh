#!/usr/bin/env bash

SUBMODULES=$(git submodule status | awk '{print $2}' | cut -d'/' -f2)

for SUBMODULE in $SUBMODULES; do
  echo "Updating $SUBMODULE"
  cd "submodules/$SUBMODULE"
  git fetch
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

if git diff --cached --quiet; then
  echo "No changes to commit"
else
  git add submodules
  git commit -m "Update submodules"
fi