skip_global_compinit=1

# common
export FIGNORE=DS_Store
export EDITOR=$(which vim)
export DOTFILES_DIR=~/.dotfiles

# paths
export PATH="/Users/dank0/.local/bin:$PATH"

# java
export JAVA_HOME=$(/usr/libexec/java_home)
export PATH=$JAVA_HOME/bin:$PATH

# read environment variables from .env
set -o allexport
source $DOTFILES_DIR/.env
set +o allexport
