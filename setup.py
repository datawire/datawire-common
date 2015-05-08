from distutils.core import setup

setup(name='datawire',
      version='0.2',
      description='Infrastructure for dataflow-driven, resilient microservices',
      author='datawire.io',
      author_email='hello@datawire.io',
      url='http://www.datawire.io',
      py_modules=['common', 'service'],
      packages=['datawire'],
      scripts=['directory', 'dw', 'splitter', 'arc']
      )
