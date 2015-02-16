Installation
============

datawire-XX/
 bin/
  Contains links to ../lib/{dw,directory,splitter} (make sure the links are relative)
 include/
 lib/
  Contains dw, directory, spliiter, and the datawire package
  Also, camke should point -DPYTHON_SITEARCH_PACKAGES to here
 share/

PYTHON_SITE_ROOT/lib/pythonX.Y/site-packages/
 contains symlink to datawire-XX/lib/cproton.py
 contains symlink to datawire-XX/lib/_cproton.so
 contains symlink to datawire-XX/lib/proton
 contains symlink to datawire-XX/lib/datawire
