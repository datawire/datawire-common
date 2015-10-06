from setuptools import setup

metadata = {}
with open("datawire/_metadata.py") as fp:
    exec(fp.read(), metadata)

setup(name='datawire-common',
      version=metadata["__version__"],
      description=metadata["__summary__"],
      author=metadata["__author__"],
      author_email=metadata["__email__"],
      url=metadata["__uri__"],
      license=metadata["__license__"],
      packages=['datawire'],
      install_requires=['python-qpid-proton >= 0.9.1.1'],
      scripts=['directory', 'dw', 'manifold'])
