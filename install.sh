#!/bin/sh

# Datawire installation script
RELEASE="0.1"

# Check OS
UNAME=$(uname)
if [ "$UNAME" != "Linux" -a "$UNAME" != "Darwin" ] ; then
     echo "This OS is not currently supported."
     exit 1
fi

# Display everything on stderr.
exec 1>&2

INSTALL_DIR="datawire-${RELEASE}"
WORKDIR=$PWD

rm -rf "$INSTALL_DIR"
mkdir "$INSTALL_DIR"

CMAKE_URL="http://www.cmake.org/files/v3.1/cmake-3.1.2-Linux-x86_64.tar.gz"
PROTON_BRANCH="0.9-alpha-1"
PROTON_URL="https://github.com/apache/qpid-proton/archive/${PROTON_BRANCH}.zip"
PROTON_DIR="qpid-proton-${PROTON_BRANCH}"
DW_URL="http://www.datawire.io/datawire-0.1.tar.gz"


# Install cmake if necessary
if command -v cmake >/dev/null; then
    echo "Found cmake ..."
    CMAKE_HOME=""
else
    echo "No cmake found ... installing ..."
    curl --progress-bar --fail "$CMAKE_URL" | tar -xzf - -C "$INSTALL_DIR" -o
    CMAKE_HOME="$INSTALL_DIR/cmake-3.1.2-Linux-x86_64/bin/"
fi

echo "Installing Qpid Proton ..."
# GitHub does a redirect from the download URL, so we use the -L option
# Force tarball to be put into PROTON_DIR
curl --progress-bar --fail -L "$PROTON_URL" -o proton.zip
unzip proton.zip -d "$INSTALL_DIR"
mkdir "$INSTALL_DIR/$PROTON_DIR/build"
cd "$INSTALL_DIR/$PROTON_DIR/build"
${CMAKE_HOME}cmake .. -DCMAKE_INSTALL_PREFIX="datawire-${RELEASE}" -DSYSINSTALL_BINDINGS=OFF -DBUILD_TESTING=OFF -DBUILD_JAVA=OFF -DBUILD_PERL=OFF
make


echo "Installing Datawire ..."
cd $WORKDIR
curl --progress-bar --fail "$DW_URL" | tar -xzf - -C "$INSTALL_DIR" -o

# Remove source

# save install manifest somewhere
# user level site packages
