# Copyright (C) k736, inc. All Rights Reserved.
# Unauthorized copying or redistribution of this file is strictly prohibited.

from roy import build, deps

class Datawire:

    def __init__(self):
        self.name = "datawire"
        self.build_deps = []
        self.deps = [deps.datawire_proton]
        self.version = "0.2"

    def setup(self, env):
        env.system("cd %s; git archive --remote git@bitbucket.org:datawireio/server.git --format=tar --prefix=datawire/ master | tar -xf -" % env.work)

    def build(self, distro):
        result = """
set -e
cd datawire
mkdir -p /work/install/opt/datawire/lib
cp -r directory dw sherlock watson datawire /work/install/opt/datawire/lib
mkdir -p /work/install/usr/bin
"""
        for script in ["directory", "dw", "sherlock", "watson"]:
            result += """
sed -i -e '1s@.*@#!/usr/bin/python2.7@' /work/install/opt/datawire/lib/%(script)s
cat > /work/install/usr/bin/%(script)s <<LAUNCHER
#!/bin/bash
export PYTHONPATH=/opt/datawire/lib/proton/bindings/python
exec /opt/datawire/lib/%(script)s "\$@"
LAUNCHER
chmod a+x /work/install/usr/bin/%(script)s
""" % {"script": script}

        result += """
cp -r deploy/common/* /work/install
cp -r deploy/%(system)s-*/* /work/install
""" % {"system": distro.image}

        return result

build(Datawire())
