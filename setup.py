from distutils.core import setup

setup(name='datawire',
      version='0.1',
      description='Infrastructure for dataflow-driven, resilient microservices',
      author='datawire.io',
      url='http://www.datawire.io',
      py_modules=['common', 'service', 'stream', 'container', 'linker'],
      scripts=['directory', 'dw', 'splitter', 'arc']
      )
