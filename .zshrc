ZSH_THEME="default"

plugins=(
  kubectl
  zsh-autosuggestions
  zsh-syntax-highlighting
)

fpath+=${ZSH_CUSTOM}/plugins/zsh-completions/src

if command -v pyenv >/dev/null; then
  eval "$(pyenv init -)";
  eval "$(pyenv virtualenv-init -)";
fi

source $DOTFILES_DIR/.aliases
source $DOTFILES_DIR/.functions
source $ZSH/oh-my-zsh.sh
