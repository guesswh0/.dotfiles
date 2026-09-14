# locale
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
export NLS_LANG=AMERICAN_AMERICA.AL32UTF8

# native brew
if [ -x /opt/homebrew/bin/brew ]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
fi
