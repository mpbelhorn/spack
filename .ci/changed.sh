#!/bin/bash

if [ ! -n "$HOST" ]; then
  echo "HOST variable not set for build job. Exiting."
  exit 1
fi

declare -a files
files=( $(git diff --name-only nccs-specific -- etc/nccs-sw-ci/$HOST) )
if [ -n "$files" ]; then
  affected=".ci/affected.${HOST}"
  echo "$CI_BUILD_ID" > "$affected"
  echo "Next stages triggered for $HOST due to changes in:"
  for f in ${files[@]}; do
    echo "    $f"
    echo "$f" >> "$affected"
  done
  exit 0
else
  echo "No changes detected for $HOST."
  exit 1
fi

