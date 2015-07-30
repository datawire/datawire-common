from setuptools import setup

def version():
    import os
    path = os.path.join(os.path.dirname(__file__), "datawire/__init__.py")
    with open(path) as f:
        for line in f:
            if "__version__" in line:
                g = {}
                l = {}
                exec line in g, l
                return l["__version__"]
    return None

setup(name='datawire-common',
      version=version(),
      description='Infrastructure for dataflow-driven, resilient microservices',
      author='datawire.io',
      author_email='hello@datawire.io',
      url='http://www.datawire.io',
      packages=['datawire'],
      install_requires=['python-qpid-proton >= 0.9.1.1'],
      scripts=['directory', 'dw', 'manifold'])
