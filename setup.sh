#!/bin/bash

export DOTFILES_DIR=$HOME/.dotfiles
export ZSH_CUSTOM=$HOME/.oh-my-zsh/custom

# nerd-fonts
curl -L -o /tmp/nerd.zip https://github.com/ryanoasis/nerd-fonts/releases/download/v2.1.0/Hack.zip
unzip /tmp/nerd.zip -d ~/Library/Fonts

# pyenv 
git clone https://github.com/pyenv/pyenv.git $HOME/.pyenv
git clone --depth 1 https://github.com/pyenv/pyenv-virtualenv.git $HOME/.pyenv/plugins/pyenv-virtualenv

# oh-my-zsh
git clone https://github.com/ohmyzsh/ohmyzsh.git ~/.oh-my-zsh

# plugins
git clone --depth 1 https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM}/plugins/zsh-syntax-highlighting
git clone --depth 1 https://github.com/zsh-users/zsh-completions ${ZSH_CUSTOM}/plugins/zsh-completions
git clone --depth 1 https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM}/plugins/zsh-autosuggestions

# theme
curl -L -o ${ZSH_CUSTOM}/themes/default.zsh-theme \
    https://gist.githubusercontent.com/guesswh0/3a4b7ca585a6e81e397f3804f3a6268a/raw/c2651f12e18b8bf5b44eb08e21c1c0796e8d1387/agnoster.zsh-theme

# bunch of symlinks
ln -sfv "$DOTFILES_DIR/.vimrc" ~
ln -sfv "$DOTFILES_DIR/.zshrc" ~
ln -sfv "$DOTFILES_DIR/.zshenv" ~
ln -sfv "$DOTFILES_DIR/.zprofile" ~
ln -sfv "$DOTFILES_DIR/.hushlogin" ~

# brew
if read -q "choice?Install packages? [y/n]:"; then
    $DOTFILES_DIR/brews.sh
fi

echo -e "\nDone. Reload your terminal."