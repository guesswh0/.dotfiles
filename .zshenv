skip_global_compinit=1

# history
export HISTSIZE=999999
export SAVEHIST=999999

# common
export FIGNORE=DS_Store
export EDITOR=vim
export DOTFILES_DIR=~/.dotfiles

# paths
export PATH="$HOME/.local/bin:$PATH"

# java
if JAVA_HOME=$(/usr/libexec/java_home 2>/dev/null); then
    export JAVA_HOME
    export PATH="$JAVA_HOME/bin:$PATH"
fi

# https://docs.astral.sh/uv/configuration/environment
export UV_PROJECT_ENVIRONMENT=".nosync/venv"
export UV_VENV_SEED=1
export UV_PYTHON="3.14"
export UV_ENV_FILE=".env"

# claude
export CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY=1
export CLAUDE_CODE_NEW_INIT=1

# kube config
if [ -d "$HOME/.kube" ]; then
	export KUBECONFIG=$(find "$HOME/.kube" -type f -name "*.yaml" | tr '\n' ':')
fi

if [ -r "$DOTFILES_DIR/.secrets" ]; then
    source "$DOTFILES_DIR/.secrets"
fi
