#!/bin/bash
# pass in server, analyzer, or redirector

# Bootstrap AMI

# (run as root)
mkdir tmp
cd tmp

# Proton
git clone git://git.apache.org/qpid-proton.git
cd qpid-proton
mkdir build
cd build
cmake .. -DCMAKE_INSTALL_PREFIX=/usr -DSYSINSTALL_BINDINGS=ON -DBUILD_PHP=OFF -DBUILD_JAVA=OFF -DBUILD_RUBY=OFF -DBUILD_
PERL=OFF
make install

# Kinetic
git clone https://kineticbot:M6P-AqJ-UEe-bB9@bitbucket.org/gokinetic/server.git
cd server
./$1