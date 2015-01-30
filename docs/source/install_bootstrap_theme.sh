#!/bin/bash

TEMP=$(mktemp -d tmp.XXXXXXXXXX)
echo $TEMP
git clone -b datawire https://github.com/datawire/sphinx-bootstrap-theme.git $TEMP
ORIGIN=$(pwd)
cd $TEMP
sudo python setup.py install
cd $ORIGIN
sudo rm -rf $TEMP
