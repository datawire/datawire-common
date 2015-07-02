import os, sys, tempfile
from argparse import ArgumentParser
from collections import defaultdict

# TODO: factor out common patterns from pkg-* files and add them as
#       utilities here

class Dep:

    def __init__(self, name, dev=False):
        self.name = name
        self._dev = dev

    @property
    def dev(self):
        return Dep(self.name, True)

    def __cmp__(self, other):
        return cmp((self.name, self._dev), (other.name, other._dev))

    def __hash__(self):
        return hash((self.name, self._dev))

class _deps:

    def __getattr__(self, name):
        return Dep(name)

deps = _deps()

def system(cmd):
    st = os.system(cmd)
    if st != 0:
        print "command failed:", cmd
        sys.exit(st)

def _dimage(ctx, tag, text, update):
    dfile = os.path.join(ctx, "Dockerfile")
    f = open(dfile, "w")
    f.write(text)
    f.close()
    opts = ""
    if update:
        opts += "--no-cache"
    system("docker build %s -t %s %s" % (opts, tag, ctx))

class Distro:

    def __init__(self):
        self.aliases = defaultdict(list)
        self.bootstrap_deps = [deps.ruby.dev, deps.gcc, deps.make]

    def configure(self, output):
        self.output = output
        self.dist = os.path.join(output, self.image)
        self.build = os.path.join(self.dist, "build")
        self.work = os.path.join(self.dist, "work")
        self.test = os.path.join(self.dist, "test")

    def prep(self):
        for d in (self.build, self.work, self.test):
            if not os.path.exists(d):
                os.makedirs(d)
            assert os.path.isdir(d)

    def images(self, config, update):
        bimg = "%s-build" % self.image
        timg = "%s-test" % self.image
        _dimage(self.build, bimg, self.build_image(config), update)
        _dimage(self.test, timg, self.test_image(config), update)
        return bimg, timg

    def run(self, image, script):
        run = os.path.join(self.dist, "run.sh")
        f = open(run, "w")
        f.write("#!/bin/bash\n")
        f.write(script)
        f.close()
        system("chmod a+x %s" % run)
        system("docker run --entrypoint=/run.sh --privileged=true -v %s:/run.sh -v %s:/work %s" %
               (os.path.abspath(run), os.path.abspath(self.work), image))

    def alias(self, dep, *values):
        self.aliases[dep].extend(values)

    def default(self, dep):
        if dep._dev:
            return "%s-%s" % (dep.name.replace("_", "-"), self.dev)
        else:
            return dep.name.replace("_", "-")

    def render(self, deps, prefix=""):
        expanded = []
        for d in deps:
            if d in self.aliases:
                expanded.extend(self.aliases[d])
            else:
                expanded.append(self.default(d))

        return " ".join([prefix + e for e in expanded])

    def build_image(self, config):
        result = """FROM %(image)s
RUN %(pkg)s -y update
RUN %(pkg)s -y install curl
RUN curl -s https://packagecloud.io/install/repositories/datawire/staging/script.%(ext)s.sh | bash
RUN %(makecache)s && %(pkg)s -y install %(bootstrap_deps)s && gem install fpm
"""
        if config.build_deps:
            result += """
RUN %(pkg)s -y install %(build_deps)s
"""
        result = result % {
            "image": self.image,
            "pkg": self.pkg,
            "ext": self.ext,
            "bootstrap_deps": self.render(self.bootstrap_deps),
            "build_deps": self.render(config.build_deps),
            "makecache": self.makecache
        }
        return result

    def test_image(self, config):
        return """FROM %(image)s
RUN %(pkg)s -y update
RUN %(pkg)s -y install curl
RUN curl -s https://packagecloud.io/install/repositories/datawire/staging/script.%(ext)s.sh | bash
RUN %(makecache)s && %(pkg)s -y install %(deps)s
""" % {
    "image": self.image,
    "pkg": self.pkg,
    "ext": self.ext,
    "deps": self.render(config.deps),
    "makecache": self.makecache
}


class Ubuntu(Distro):

    def __init__(self):
        Distro.__init__(self)
        self.alias(deps.ssl, "libssl1.0.0")
        self.alias(deps.ssl.dev, "libssl-dev")
        self.alias(deps.uuid, "libuuid1")
        self.alias(deps.uuid.dev, "uuid-dev")
        self.alias(deps.python, "python2.7", "libpython2.7")
        self.image = "ubuntu"
        self.pkg = "apt-get"
        self.ext = "deb"
        self.dev = "dev"
        self.makecache = "apt-get update"

class Centos(Distro):

    def __init__(self):
        Distro.__init__(self)
        self.alias(deps.ssl, "openssl-libs")
        self.alias(deps.ssl.dev, "openssl-devel")
        self.alias(deps.uuid, "libuuid")
        self.alias(deps.uuid.dev, "libuuid-devel")
        self.alias(deps.policycoreutils, "policycoreutils", "policycoreutils-python")
        self.image = "centos"
        self.pkg = "yum"
        self.ext = "rpm"
        self.dev = "devel"
        self.bootstrap_deps += [deps.rpm_build]
        self.makecache = "yum makecache --disablerepo='*' --enablerepo=datawire_staging"

class Env:

    def __init__(self, work):
        self.work = work

    def system(self, cmd):
        system(cmd)

def build(package):
    parser = ArgumentParser(prog="roy")
    parser.add_argument("-o", "--output", default="dist", help="output directory")
    parser.add_argument("-i", "--images", action="store_true", help="produce images only")
    parser.add_argument("-d", "--distro", help="specify a distro (default to all)")
    parser.add_argument("-r", "--run", action="store_true", help="run a shell in the test image")
    parser.add_argument("-s", "--shell", action="store_true", help="run a shell in the build image")
    parser.add_argument("-u", "--update", action="store_true", help="update images")
    args = parser.parse_args()
    output = args.output
    if not os.path.exists(output):
        os.makedirs(output)
    if not os.path.isdir(output):
        parser.error("output must be a directory: %s" % output)

    for distro in [Centos(), Ubuntu()]:
        if args.distro and base.image != args.distro:
            continue
        distro.configure(output)

        distro.prep()
        bimg, timg = distro.images(package, args.update)
        if args.images:
            continue

        if args.run or args.shell:
            if args.shell:
                shimg = bimg
            else:
                shimg = timg
            print
            print "IMAGE:", shimg
            print
            os.system("docker run --privileged=true -it -v %s:/dist %s /bin/bash" %
                      (os.path.abspath(output), shimg))
            continue

        distro.run(bimg, "rm -rf /work/*")
        package.setup(Env(distro.work))
        buildsh = "cd /work\n"
        buildsh += package.build(distro)
        buildsh += "\ncd /work\n"
        opts = ""
        for c in getattr(package, "conf", []):
            opts += " --config-files %s" % c
        if hasattr(package, "postinstall"):
            opts += " --after-install /tmp/postinstall"
            buildsh += """cat > /tmp/postinstall <<POSTINSTALL
%s
POSTINSTALL
""" % package.postinstall
        buildsh += "\nfpm -f -s dir -t %(ext)s -n %(name)s -v %(version)s -a %(arch)s %(deps)s %(opts)s -C/work/install .\n" % {
            "ext": distro.ext,
            "name": package.name,
            "version": package.version,
            "arch": getattr(package, "arch", "native"),
            "deps": distro.render(package.deps, prefix="-d "),
            "opts": opts
        }
        distro.run(bimg, buildsh)
        distro.run(bimg, "chown -R %s:%s /work" % (os.getuid(), os.getgid()))
        system("mv %s/*.%s %s" % (distro.work, distro.ext, output))
