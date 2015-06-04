#/bin/sh

VERSION=0.2
TARGET=/var/www/html

mkdir -p $TARGET

python setup.py sdist
cp -f dist/datawire-${VERSION}.tar.gz ${TARGET}/
cp -f install.sh ${TARGET}/

cd docs
make html
rm -rf ${TARGET}/docs
mkdir ${TARGET}/docs
mv build/html/* ${TARGET}/docs/
