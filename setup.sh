#!/bin/bash

set -euo pipefail

DOTFILES_DIR="$HOME/.dotfiles"

link() {
    [ "$1" -ef "$2" ] && return
    if [ -e "$2" ] || [ -L "$2" ]; then
        mv "$2" "$2.backup.$(date +%Y%m%d%H%M%S).$$"
    fi
    ln -sv "$1" "$2"
}

read -r -p 'Install packages? [y/N]: ' choice
if [[ "$choice" == [yY] ]]; then
    bash "$DOTFILES_DIR/brews.sh"
    bash "$DOTFILES_DIR/tools.sh"
fi

download_dir=$(mktemp -d)
trap 'rm -rf "$download_dir"' EXIT

if [ ! -s "$HOME/.vim/autoload/plug.vim" ]; then
    curl -fsSL https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim \
        -o "$download_dir/plug.vim"
    mkdir -p "$HOME/.vim/autoload"
    install -m 644 "$download_dir/plug.vim" "$HOME/.vim/autoload/plug.vim"
fi

if [ ! -s "$HOME/.local/share/antigen/antigen.zsh" ]; then
    curl -fsSL https://raw.githubusercontent.com/zsh-users/antigen/v2.2.3/bin/antigen.zsh \
        -o "$download_dir/antigen.zsh"
    mkdir -p "$HOME/.local/share/antigen"
    install -m 644 "$download_dir/antigen.zsh" "$HOME/.local/share/antigen/antigen.zsh"
fi

for name in .vimrc .zshrc .zshenv .zprofile .hushlogin .antigenrc; do
    link "$DOTFILES_DIR/$name" "$HOME/$name"
done

read -r -p 'Install agent configuration? [y/N]: ' choice
if [[ "$choice" == [yY] ]]; then
    mkdir -p "$HOME/.agents/skills" "$HOME/.claude/skills" "$HOME/.codex"
    link "$DOTFILES_DIR/.agents/AGENTS.md" "$HOME/.claude/CLAUDE.md"
    link "$DOTFILES_DIR/.agents/AGENTS.md" "$HOME/.codex/AGENTS.md"
    for skill in "$DOTFILES_DIR"/.agents/skills/*/; do
        [ -f "$skill/SKILL.md" ] || continue
        skill=${skill%/}
        link "$skill" "$HOME/.agents/skills/${skill##*/}"
        link "$skill" "$HOME/.claude/skills/${skill##*/}"
    done
fi

printf '\nDone. Open a new terminal.\n'
