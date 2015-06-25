# Copyright (C) k736, inc. All Rights Reserved.
# Unauthorized copying or redistribution of this file is strictly prohibited.

from roy import build, deps

class Proton:

    def __init__(self):
        self.name = "datawire-proton"
        self.build_deps = [deps.patch, deps.cmake, deps.uuid.dev, deps.ssl.dev,
                           deps.swig, deps.python.dev]
        self.deps = [deps.uuid, deps.ssl, deps.python]
        self.version = "0.9-datawire-1"

    def setup(self, env):
        env.system("wget -nv https://github.com/datawire/qpid-proton/archive/0.9-datawire-1.zip -O %s/proton.zip" % env.work)
        env.system("cd %s; unzip -o proton.zip" % env.work)
        env.system("cd %s; mv qpid-proton-0.9-datawire-1 proton" % env.work)

    def build(self, distro):
        result = """
set -e

cd proton

patch -s CMakeLists.txt <<CMAKEPATCH
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

mkdir -p build
cd build
cmake .. -DCMAKE_INSTALL_PREFIX=/opt/datawire -DLIB_SUFFIX=""
make && make install DESTDIR=/work/install
"""
        return result

build(Proton())
