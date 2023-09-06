# antigen
source ~/.antigenrc

source $DOTFILES_DIR/.aliases
source $DOTFILES_DIR/.functions

# shell integration
source $HOME/.iterm2_shell_integration.zsh

# pyenv
if command -v pyenv >/dev/null; then
  eval "$(pyenv init -)";
  eval "$(pyenv virtualenv-init -)";
fi
