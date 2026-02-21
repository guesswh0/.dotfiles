# antigen
source ~/.antigenrc

source $DOTFILES_DIR/.aliases
source $DOTFILES_DIR/.functions

# shell integration
if [ -r "$HOME/.iterm2_shell_integration.zsh" ]; then
	source "$HOME/.iterm2_shell_integration.zsh"
fi

# zsh completions
FPATH="$(brew --prefix)/share/zsh/site-functions:${FPATH}"
