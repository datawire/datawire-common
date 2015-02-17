#/bin/sh

python setup.py sdist
cp -f dist/datawire-0.1.tar.gz /var/www/html/
cp -f install.sh /var/www/html/

cd docs
make html
rm -rf /var/www/html/docs
mkdir /var/www/html/docs
mv build/html/* /var/www/html/docs/
