#amara3 namespace package

#Following line is setuptools style namespace package decl, but we're only reluctantly using setuptools, so avoid this
#__import__('pkg_resources').declare_namespace(__name__)

# A Python "namespace package" http://www.python.org/dev/peps/pep-0382/
# This always goes inside of a namespace package's __init__.py

from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)
