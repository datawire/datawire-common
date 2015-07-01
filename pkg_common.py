# Copyright (C) k736, inc. All Rights Reserved.
# Unauthorized copying or redistribution of this file is strictly prohibited.

class Common:

    def setup(self, env):
        env.system("git archive --format=tar --prefix=datawire/ HEAD | (cd %s && tar -xf -)" % env.work)

    def install_prep(self):
        return """
set -e
cd datawire
mkdir -p /work/install/opt/datawire/lib
mkdir -p /work/install/usr/bin
"""

    def install_script(self, script):
        return """
cp %(script)s /work/install/opt/datawire/lib
sed -i -e '1s@.*@#!/usr/bin/python2.7 -u@' /work/install/opt/datawire/lib/%(script)s
cat > /work/install/usr/bin/%(script)s <<LAUNCHER
#!/bin/bash
export PYTHONPATH=/opt/datawire/lib/proton/bindings/python
exec /opt/datawire/lib/%(script)s "\$@"
LAUNCHER
chmod a+x /work/install/usr/bin/%(script)s
""" % {"script": script}

    def install_config(self, dir, system=None):
        result = """
cp -r deploy/%(dir)s/common/* /work/install
"""
        if system:
            result += """
cp -r deploy/%(dir)s/%(system)s-*/* /work/install
"""
        return result % {"system": system or None, "dir": dir}
