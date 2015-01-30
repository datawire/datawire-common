Documentation
=============

Documentation is written using Sphinx.  You must have [Sphinx installed](http://sphinx-doc.org/latest/install.html) to build the documentation.

In addition, Sphinx can only build the documentation if the latest version of the datawire modules are installed on the host machine.  To install the latest version of the modules and build the HTML documentation, run:

```sh
(make install && make html)
```

You may need to run `make install` as root.

The documentation will be built in the build directory.

In order to use the bootstrap theme for Sphinx, you need to have the Sphinx bootstrap theme package installed.
To install it, you can run the install\_bootstrap\_theme.sh script.
Otherwise, Sphinx will default to the default theme.

Example Tags
============

You can have put python files in source/examples which can be referenced as examples from within the documentation/tutorials.
To make a named tag within an example python file, use a line of the form `# <tag_name>` to begin the tag (where `tag_name` is replaced with the name of the tag) and a line of the form `# </tag_name>` to end the tag.
Tags *do not* have to be properly nested.

Upon build, tags will be preprocessed into new source files in the source/tags directory.
If the example file was called source/examples/example1.py and contained the tags `hello`, `world`, and `python`, the files in the tags directory after preprocessing would be source/tags/example1.py, source/tags/example1.py.hello.py, source/tags/example1.py.world.py, and source/tags/example1.py.python.py

**NOTE**:  *Files in source/tags are automatically generated and should never be editted directly*.

To show the source of one of the tags files in a documentation file (.rst), use the syntax:

```
.. literalinclude:: ../tags/example1.py.hello.py
```

(with the path replaced appropriately).

Example:

source/examples/test.py:

```python
# hello
# <tag3>
# <tag1>
# A comment
print "Hello world!"
# </tag1>
# <tag2>
# Another comment
print "hello world2!"
# </tag3>
# </tag2>
```
