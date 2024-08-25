skip_global_compinit=1

# common
export FIGNORE=DS_Store
export EDITOR=$(which vim)
export DOTFILES_DIR=~/.dotfiles

# java
export JAVA_HOME=$(/usr/libexec/java_home)
export PATH=$JAVA_HOME/bin:$PATH

# pyenv
export PYENV_ROOT=~/.pyenv
export PATH=$PYENV_ROOT/bin:$PATH
export PYENV_VIRTUALENV_DISABLE_PROMPT=1

# read environment variables from .env
export $(grep -v '^#' "$DOTFILES_DIR/.env" | xargs)
