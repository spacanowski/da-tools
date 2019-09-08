#!/bin/sh

cd hooks || exit

if [ -z "$1" ]; then
  echo 'Specify projects dir!'
  exit 1
fi

for j in $1/* ; do
  if [ ! -d "$j/.git" ]; then
    # Not a git repo
    echo "$j is not a git repo"
    continue
  fi

  echo "Installing git hooks for $j repo"

  HOOK_DIR=$j/.git/hooks
  mkdir -p "$HOOK_DIR"

  for i in * ; do
    cp "$(pwd)/$i" "$HOOK_DIR/$i"
    chmod a+x "$i" "$HOOK_DIR/$i"
  done
done
