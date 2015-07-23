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

class Distro:

    def __init__(self):
        self.aliases = defaultdict(list)
        self.bootstrap_deps = [deps.ruby.dev, deps.gcc, deps.make]

    def configure(self, output):
        self.output = output
        self.dist = os.path.join(output, self.image)
        self.build = os.path.join(self.dist, "build")
        self.work = os.path.join(self.dist, "work")
        self.pack = os.path.join(self.dist, "pack")

    def prep(self):
        for d in (self.build, self.work, self.pack):
            if not os.path.exists(d):
                os.makedirs(d)
            assert os.path.isdir(d)

    def _dimage(self, ctx, tag, text, update):
        if isinstance(text, tuple):
            text, files = text
        else:
            files = {}

        for name, content in [("Dockerfile", text)] + files.items():
            dfile = os.path.join(ctx, name)
            f = open(dfile, "w")
            f.write(content)
            f.close()
        opts = ""
        if update:
            opts += "--no-cache"
        system("docker build %s -t %s %s" % (opts, tag, ctx))

    def images(self, config, update):
        bimg = "%s-build" % self.image
        pimg = "%s-pkg" % self.image
        self._dimage(self.build, bimg, self.build_image(config), update)
        self._dimage(self.pack, pimg, self.pack_image(config), update)
        return bimg, pimg

    def run(self, image, script):
        run = os.path.join(self.dist, "run.sh")
        f = open(run, "w")
        f.write("#!/bin/bash\n")
        f.write(script)
        f.close()
        system("chmod a+x %s" % run)
        system("docker run --rm --entrypoint=/run.sh --privileged=true -v %s:/run.sh -v %s:/work -v %s:/dist %s" %
               (os.path.abspath(run), os.path.abspath(self.work), os.path.abspath(self.output), image))

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

    def vars(self, config):
        return {
            "image": self.image,
            "pkg": self.pkg,
            "extrapkgopts": self.extrapkgopts,
            "ext": self.ext,
            "bootstrap_deps": self.render(self.bootstrap_deps),
            "build_deps": self.render(config.build_deps),
            "deps": self.render(config.deps),
            "repopath": self.repopath,
            "repocfg": self.repocfg,
            "createrepo": self.createrepo
        }

    def pack_image(self, config):
        return """FROM %(image)s
RUN %(pkg)s -y update
RUN %(pkg)s -y install %(bootstrap_deps)s && gem install fpm
""" % self.vars(config)

    def build_image(self, config):
        result = """FROM %(image)s
RUN %(pkg)s -y update
ADD repo.txt %(repopath)s
"""
        return result % self.vars(config), {"repo.txt": self.repocfg}

class Ubuntu(Distro):

    def __init__(self):
        Distro.__init__(self)
        self.alias(deps.ssl, "libssl1.0.0")
        self.alias(deps.ssl.dev, "libssl-dev")
        self.alias(deps.uuid, "libuuid1")
        self.alias(deps.uuid.dev, "uuid-dev")
        self.alias(deps.python, "python2.7", "libpython2.7")
        self.image = "ubuntu"
        self.repopath = "/etc/apt/sources.list.d/roy.list"
        self.repocfg = """
deb file:/work/repo ./
"""
        self.createrepo = "cd /work/repo && dpkg-scanpackages . /dev/null | gzip -9c > Packages.gz"
        self.pkg = "apt-get"
        self.extrapkgopts = "--force-yes"
        self.ext = "deb"
        self.dev = "dev"
        self.bootstrap_deps += [deps.dpkg_dev]

class Centos(Distro):

    def __init__(self):
        Distro.__init__(self)
        self.alias(deps.ssl, "openssl-libs")
        self.alias(deps.ssl.dev, "openssl-devel")
        self.alias(deps.uuid, "libuuid")
        self.alias(deps.uuid.dev, "libuuid-devel")
        self.alias(deps.policycoreutils, "policycoreutils", "policycoreutils-python")
        self.image = "centos"
        self.repopath = "/etc/yum.repos.d/roy.repo"
        self.repocfg = """
[roy]
name=Roy - local packages
baseurl=file:///work/repo
enabled=1
gpgcheck=0
skip_if_unavailable=true
"""
        self.createrepo = "createrepo /work/repo"
        self.pkg = "yum"
        self.extrapkgopts = ""
        self.ext = "rpm"
        self.dev = "devel"
        self.bootstrap_deps += [deps.rpm_build, deps.createrepo]

class Fedora(Centos):

    def __init__(self):
        Centos.__init__(self)
        self.image = "fedora"

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
    parser.add_argument("-s", "--shell", action="store_true", help="run a shell in the build image")
    parser.add_argument("-p", "--package", action="store_true", help="run a shell in the package image")
    parser.add_argument("-u", "--update", action="store_true", help="update images")
    args = parser.parse_args()
    output = args.output
    if not os.path.exists(output):
        os.makedirs(output)
    if not os.path.isdir(output):
        parser.error("output must be a directory: %s" % output)

    for distro in [Centos(), Ubuntu(), Fedora()]:
        if args.distro and distro.image != args.distro:
            continue
        distro.configure(output)

        distro.prep()
        bimg, pimg = distro.images(package, args.update)
        if args.images:
            continue

        if args.shell or args.package:
            if args.shell:
                shimg = bimg
            else:
                shimg = pimg
            print
            print "IMAGE:", shimg
            print
            os.system("docker run --rm --entrypoint=/bin/bash --privileged=true -it -v %s:/work -v %s:/dist %s" %
                      (os.path.abspath(distro.work), os.path.abspath(output), shimg))
            continue

        distro.run(pimg, "rm -rf /work/*")
        distro.run(pimg, """
mkdir /work/repo
cp /dist/%(image)s/*.%(ext)s /work/repo/
%(createrepo)s
        """ % distro.vars(package))
        package.setup(Env(distro.work))
        buildsh = "%(pkg)s -y update\n"
        if package.build_deps:
            buildsh += "%(pkg)s -y %(extrapkgopts)s install %(build_deps)s\n"
        buildsh += "cd /work\n"
        buildsh = buildsh % distro.vars(package)
        buildsh += package.build(distro)
        fpmsh = "cd /work\n"
        opts = ""
        for c in getattr(package, "conf", []):
            opts += " --config-files %s" % c
        if hasattr(package, "postinstall"):
            opts += " --after-install /tmp/postinstall"
            fpmsh += """cat > /tmp/postinstall <<POSTINSTALL
%s
POSTINSTALL
""" % package.postinstall
        opts += " --iteration %s" % getattr(package, "iteration", 1)
        fpmsh += "\nfpm -f -s dir -t %(ext)s -n %(name)s -v %(version)s -a %(arch)s %(deps)s %(opts)s -C/work/install .\n" % {
            "ext": distro.ext,
            "name": package.name,
            "version": package.version,
            "arch": getattr(package, "arch", "native"),
            "deps": distro.render(package.deps, prefix="-d "),
            "opts": opts
        }
        distro.run(bimg, buildsh)
        distro.run(pimg, fpmsh)
        distro.run(pimg, "chown -R %s:%s /work" % (os.getuid(), os.getgid()))
        system("mv %s/*.%s %s" % (distro.work, distro.ext, distro.dist))
