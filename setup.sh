#!/bin/sh

DOTFILES_DIR=~/.dotfiles

# nerd-fonts
curl -L -o /tmp/nerd.zip https://github.com/ryanoasis/nerd-fonts/releases/download/v2.1.0/Hack.zip
unzip /tmp/nerd.zip -d ~/Library/Fonts

# vim-plug
curl -fLo ~/.vim/autoload/plug.vim --create-dirs \
    https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim

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