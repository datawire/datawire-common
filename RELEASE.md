###Release nomenclature:

Releases are tagged with the release, e.g. "0.3", or "0.3.1". Release
branches should end in ".x" so that they won't coincide with release
tags, e.g. "0.3.x".

###Release steps:

1. Create a branch <primary>.<secondary>.x unless it already exists.
   This can be deferred until point releases are needed if master is
   releasable.
2. Build and test the release:
  1. python setup.py bdist_wheel
  2. spin up a clean test machine (e.g. use ec2 or vagrant or docker,
     or just sacrifice your local laptop to the gods of testing)
  3. copy dist/datawire_common-<blah>.whl to the test machine
  4. on test machine:
     - install python and pip
     - note, proton pip install requires these packages and does not fail gracefully when they are not present:
       pkg-config, uuid (uuid-dev on ubuntu, libuuid-devel on fedora/rhel systems), swig, python-dev/devel
     # pip install datawire_common-<blah.whl>

    root@326e32ef1d75:/# dw route list
    Could not connect to directory '//localhost/directory' (attempt 1)
    Could not connect to directory '//localhost/directory' (attempt 2)
    Could not connect to directory '//localhost/directory' (attempt 3)
    Could not connect to directory '//localhost/directory' (attempt 4)
    Could not connect to directory '//localhost/directory' (attempt 5)
    Unable to connect to directory '//localhost/directory'
    root@326e32ef1d75:/# ls /usr/local/bin/
    directory  dw  manifold
    root@326e32ef1d75:/# directory &
    [1] 4686
    root@326e32ef1d75:/# 2015-07-29 17:08:25 directory root WARNING No host configured. Falling back to localhost.
    root@326e32ef1d75:/# dw route list
    (no routes)
    root@326e32ef1d75:/# 
     ... do more testing ...

3. Create a tag.
4. Upload to pypi

###Building packages:

These steps require docker to be installed.

1. Building installable packages for proton: ./pkg-proton
2. Building installable packages for datawire: ./pkg-datawire
3. Look in dist/<os> for the appropriate packages and push to a repo
   of your choice.

Note that the rpm package name for datawire-common is actually
datawire-directory, this will be reconciled at some point.
