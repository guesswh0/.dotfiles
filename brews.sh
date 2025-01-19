#!/bin/sh

# install brew
if ! [ -x "$(command -v brew)" ]; then
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# arm64 brew
if [ $(uname -m) = "arm64" ]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
fi

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

# kubernetes
brew install helm
brew install kubectl
brew install minikube
brew install kubectx

# basic apps
brew install --cask dash
brew install --cask iina
brew install --cask clipy
brew install --cask typora
brew install --cask transmission
brew install --cask google-chrome
brew install --cask syntax-highlight
brew install --cask browserosaurus

# dev apps
brew install --cask iterm2
brew install --cask docker
brew install --cask postman
brew install --cask mongodb-compass
brew install --cask pycharm
brew install --cask dbeaver-community
