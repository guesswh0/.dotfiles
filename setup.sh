#!/bin/sh

DOTFILES_DIR=~/.dotfiles

# nerd-fonts
curl -L -o /tmp/nerd.zip https://github.com/ryanoasis/nerd-fonts/releases/download/v2.1.0/Hack.zip
unzip /tmp/nerd.zip -d ~/Library/Fonts

# vim-plug
curl -fLo ~/.vim/autoload/plug.vim --create-dirs \
    https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim

# bunch of symlinks
ln -sfv $DOTFILES_DIR/.vimrc ~
ln -sfv $DOTFILES_DIR/.zshrc ~
ln -sfv $DOTFILES_DIR/.zshenv ~
ln -sfv $DOTFILES_DIR/.zprofile ~
ln -sfv $DOTFILES_DIR/.hushlogin ~
ln -sfv $DOTFILES_DIR/.antigenrc ~

# tools
if read -q "choice?Install packages? [y/n]:"; then
    $DOTFILES_DIR/brews.sh
    $DOTFILES_DIR/tools.sh
fi

echo -e "\nDone. Reload your terminal."