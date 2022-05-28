# locale
export LANG=eu_US.UTF-8
export LC_ALL=en_US.UTF-8
export NLS_LANG=AMERICAN_AMERICA.AL32UTF8

# native brew
if [ $(uname -m) = "arm64" ]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
fi

# pyenv init
eval "$(pyenv init --path)"