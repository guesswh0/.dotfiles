skip_global_compinit=1

# history
export HISTSIZE=999999
export SAVEHIST=999999

# common
export FIGNORE=DS_Store
export EDITOR=$(which vim)
export DOTFILES_DIR=~/.dotfiles

# paths
export PATH="/Users/dank0/.local/bin:$PATH"

# java
export JAVA_HOME=$(/usr/libexec/java_home)
export PATH=$JAVA_HOME/bin:$PATH

# https://docs.astral.sh/uv/configuration/environment
export UV_PROJECT_ENVIRONMENT=".nosync/venv"
export UV_VENV_SEED=1
export UV_PYTHON="3.12"
export UV_ENV_FILE=".env"

# kube config
export KUBECONFIG=$(find ~/.kube -type f -name "*.yaml" | tr '\n' ':')