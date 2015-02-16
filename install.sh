#!/bin/sh

# Datawire installation script
RELEASE="0.1"
WORK_DIR=$PWD

# Check OS
UNAME=$(uname)
if [ "$UNAME" != "Linux" -a "$UNAME" != "Darwin" ] ; then
     echo "This OS is not currently supported."
     exit 1
fi

# Check essential commands that aren't part of POSIX
COMMANDS="make cmake unzip tar gcc swig patch"
MISSING=""

for CMD in $COMMANDS; do
    LOC=$(type $CMD 2>/dev/null)
    if [ -z "$LOC" ]; then
	MISSING="${MISSING} ${CMD}"
    fi
done

if [[ ! -z $MISSING ]]; then
    echo "The install program did not find the following commands: "
    echo "$MISSING"
    echo "Please install this software and re-run the install script."
    exit 1
fi

# Display everything on stderr.
exec 1>&2

INSTALL_DIR="datawire-${RELEASE}"
INSTALL_LOG="${WORK_DIR}/${INSTALL_DIR}/dw-install.log"
TEMP_DIR=".datawire-temp"

rm -rf "$INSTALL_DIR" "$TEMP_DIR"
mkdir "$INSTALL_DIR"
mkdir "$TEMP_DIR"

PROTON_BRANCH="0.9-alpha-1"
PROTON_URL="https://github.com/apache/qpid-proton/archive/${PROTON_BRANCH}.zip"
PROTON_DIR="qpid-proton-${PROTON_BRANCH}"
DW_URL="http://www.datawire.io/datawire-0.1.tar.gz"
USER_SITE_DIR=$(python -m site --user-site)

echo "Downloading Qpid Proton ..."
# GitHub does a redirect from the download URL, so we use the -L option
curl --progress-bar --fail -L "$PROTON_URL" -o proton.zip
unzip proton.zip -d "$TEMP_DIR" >> $INSTALL_LOG
echo "Configuring Qpid Proton ..."

# Patch RPATH
patch -s ${WORK_DIR}/${TEMP_DIR}/${PROTON_DIR}/CMakeLists.txt <<CMAKEPATCH
--- a/CMakeLists.txt
+++ b/CMakeLists.txt
@@ -77,6 +77,8 @@ set (SYSCONF_INSTALL_DIR etc CACHE PATH "System read only configuration director
 set (SHARE_INSTALL_DIR share CACHE PATH "Shared read only data directory")
 set (MAN_INSTALL_DIR share/man CACHE PATH "Manpage directory")
 
+set (CMAKE_INSTALL_RPATH \${CMAKE_INSTALL_PREFIX}/\${LIB_INSTALL_DIR})
+
 mark_as_advanced (INCLUDE_INSTALL_DIR LIB_INSTALL_DIR SYSCONF_INSTALL_DIR SHARE_INSTALL_DIR MAN_INSTALL_DIR)
 
 ## LANGUAGE BINDINGS
CMAKEPATCH

mkdir "$TEMP_DIR/$PROTON_DIR/build"
cd "$TEMP_DIR/$PROTON_DIR/build"

cmake .. -DCMAKE_INSTALL_PREFIX="${WORK_DIR}/${INSTALL_DIR}" -DSYSINSTALL_BINDINGS=OFF -DBUILD_TESTING=OFF -DBUILD_JAVA=OFF -DBUILD_PERL=OFF -DBUILD_RUBY=OFF -DBUILD_PHP=OFF -DPYTHON_SITEARCH_PACKAGES="${WORK_DIR}/${INSTALL_DIR}/lib" >> $INSTALL_LOG
echo "Building Qpid Proton ..."
make >> $INSTALL_LOG
make install >> $INSTALL_LOG

echo "Installing Datawire ..."
cd ${WORK_DIR}/${TEMP_DIR}
curl --progress-bar --fail "$DW_URL" -o dw.tar.gz
tar -xzf dw.tar.gz
cd $INSTALL_DIR

python setup.py install --user >> $INSTALL_LOG

# Set up symlinks
cd $USER_SITE_DIR
ln -s ${WORK_DIR}/${INSTALL_DIR}/lib/cproton.py cproton.py
ln -s ${WORK_DIR}/${INSTALL_DIR}/lib/_cproton.so _cproton.so
ln -s ${WORK_DIR}/${INSTALL_DIR}/lib/proton proton
ln -s ${WORK_DIR}/${INSTALL_DIR}/lib/datawire datawire

cd ${WORK_DIR}/${INSTALL_DIR}/bin
ln -s ${WORK_DIR}/${INSTALL_DIR}/lib/dw dw
ln -s ${WORK_DIR}/${INSTALL_DIR}/lib/dw splitter
ln -s ${WORK_DIR}/${INSTALL_DIR}/lib/dw directory


# Remove source
rm -rf ${WORK_DIR}/${TEMP_DIR} ${WORK_DIR}/proton.zip

cat <<WELCOME

Welcome to Datawire!

Datawire has been installed into ${WORK_DIR}/${INSTALL_DIR}.
To get started, visit http://www.datawire.io/tutorial.
WELCOME
