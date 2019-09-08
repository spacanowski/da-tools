#!/bin/bash

name=$1
mail=$2
sed "s/<name>/${name}/g; s/<mail>/${mail}/g" .gitconfig > ~/.gitconfig
