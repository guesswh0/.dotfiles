#!/bin/sh

DOTFILES_DIR=~/.dotfiles

# nerd-fonts
wget -P ~/Library/Fonts https://github.com/ryanoasis/nerd-fonts/raw/master/patched-fonts/Hack/Regular/complete/Hack%20Regular%20Nerd%20Font%20Complete.ttf

# antigen
wget git.io/antigen -O /usr/local/opt/antigen.zsh

# pyenv 
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
git clone --depth 1 https://github.com/pyenv/pyenv-virtualenv.git ~/.pyenv/plugins/pyenv-virtualenv

# bunch of symlinks
ln -sfv $DOTFILES_DIR/.vimrc ~
ln -sfv $DOTFILES_DIR/.zshrc ~
ln -sfv $DOTFILES_DIR/.zshenv ~
ln -sfv $DOTFILES_DIR/.zprofile ~
ln -sfv $DOTFILES_DIR/.hushlogin ~
ln -sfv $DOTFILES_DIR/.antigenrc ~

# brew
if read -q "choice?Install packages? [y/n]:"; then
    $DOTFILES_DIR/brews.sh
fi

echo -e "\nDone. Reload your terminal."