if command -v brew >/dev/null 2>&1; then
    FPATH="$(brew --prefix)/share/zsh/site-functions:${FPATH}"
fi

source "$HOME/.antigenrc"

source "$DOTFILES_DIR/.aliases"
source "$DOTFILES_DIR/.functions"

# shell integration
if [ -r "$HOME/.iterm2_shell_integration.zsh" ]; then
	source "$HOME/.iterm2_shell_integration.zsh"
fi
