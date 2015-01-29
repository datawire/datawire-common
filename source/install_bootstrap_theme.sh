#!/bin/bash

TEMP=$(mktemp -d tmp.XXXXXXXXXX)
echo $TEMP
git clone https://github.com/ryan-roemer/sphinx-bootstrap-theme.git $TEMP
ORIGIN=$(pwd)
cd $TEMP
sudo python setup.py install
cd $ORIGIN
sudo rm -rf $TEMP
