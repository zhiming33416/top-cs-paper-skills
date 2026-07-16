#!/usr/bin/env sh
set -eu

repository_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec python3 "$repository_root/scripts/install_skills.py" "$@"
