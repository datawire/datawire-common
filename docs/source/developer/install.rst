Installation
============

datawire-XX/
 bin/
  Contains dw, directory, splitter
 include/
 lib/
  Contains datawire module, Proton python bindings
 lib64/
  Contains Proton library
 share/

PYTHON_SITE_ROOT/lib/pythonX.Y/site-packages/
 proton/
  contains symlink to cproton.py
  contains symlink to _cproton.so
  contains symlink to datawire-XX/lib/proton/ (Proton python bindings)
 datawire/ is direct symlink to datawire-XX/lib/datawire

 
