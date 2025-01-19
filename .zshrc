# antigen
source ~/.antigenrc

source $DOTFILES_DIR/.aliases
source $DOTFILES_DIR/.functions

# shell integration
source $HOME/.iterm2_shell_integration.zsh

# zsh completions
FPATH="$(brew --prefix)/share/zsh/site-functions:${FPATH}"
