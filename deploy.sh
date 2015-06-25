#!/bin/bash

VERSION=0.2
TARGET=/var/www/html

mkdir -p $TARGET

python setup.py sdist
cp -f dist/datawire-${VERSION}.tar.gz ${TARGET}/
cp -f install.sh ${TARGET}/

sphinx-build docs/source ${TARGET}/docs
