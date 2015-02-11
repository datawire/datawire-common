#!/bin/sh

# Datawire installation script
RELEASE="0.1"

# Check OS
# UNAME=$(uname)
# if [ "$UNAME" != "Linux" ] ; then
#     echo "This OS is not currently supported."
#     exit 1
# fi

# Display everything on stderr.
exec 1>&2

INSTALL_TMPDIR="$HOME/.dw-install-tmp"

rm -rf "$INSTALL_TMPDIR"
mkdir "$INSTALL_TMPDIR"

CMAKE_URL="http://www.cmake.org/files/v3.1/cmake-3.1.2-Linux-x86_64.tar.gz"
DW_URL="https://www.datawire.io/install/datawire-0.1.tar.gz"

# Install cmake if necessary
if command -v cmake >/dev/null; then
    echo "Found cmake ..."
else
    echo "No cmake found ... installing ..."
    curl --progress-bar --fail "$CMAKE_URL" | tar -xzf - -C "$INSTALL_TMPDIR" -o
fi

echo "Installing Datawire ..."

# Install Datawire
curl --progress-bar --fail "$DW_URL" | tar -xzf - -C "$INSTALL_TMPDIR" -o

# Proton



# Build Proton

# Build Datawire
