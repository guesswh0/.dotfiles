#!/bin/sh

# install uv
if ! [ -x "$(command -v uv)" ]; then
    brew install uv
fi

uv tool install yq
uv tool install ruff
uv tool install pre-commit