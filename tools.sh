#!/bin/bash

set -euo pipefail

if ! command -v uv >/dev/null 2>&1 && [ -x /opt/homebrew/bin/brew ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
fi
if ! command -v uv >/dev/null 2>&1; then
    printf 'Install packages with bash brews.sh first.\n' >&2
    exit 1
fi

uv tool install yq
uv tool install ruff
uv tool install pre-commit
