#!/bin/bash

set -euo pipefail

if [ ! -x /opt/homebrew/bin/brew ]; then
    installer=$(mktemp)
    trap 'rm -f "$installer"' EXIT
    curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh -o "$installer"
    /bin/bash "$installer"
fi
eval "$(/opt/homebrew/bin/brew shellenv)"

brew install --cask font-hack-nerd-font

# basic tools
brew install bat
brew install tree
brew install wget
brew install htop
brew install pwgen
brew install telnet
brew install moreutils
brew install coreutils
brew install source-highlight

# build tools
brew install cmake
brew install python
brew install pkg-config
brew install node
brew install uv
brew install jq

# dev tools
brew install postgresql
brew install redis

# kubernetes
brew install helm
brew install kubectl

# basic apps
brew install --cask dash
brew install --cask iina
brew install --cask clipy
brew install --cask typora
brew install --cask transmission
brew install --cask google-chrome
brew install --cask chatgpt
brew install --cask claude
brew install --cask wispr-flow

# dev apps
brew install --cask iterm2
brew install --cask docker-desktop
brew install --cask postman
brew install --cask aptakube
brew install --cask pycharm
brew install --cask datagrip
brew install --cask oracle-jdk
