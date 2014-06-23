# -*- coding: utf-8 -*-
from distutils.core import setup
import sys, os

versionfile = 'lib/version.py'
exec(compile(open(versionfile, "rb").read(), versionfile, 'exec'), globals(), locals())
__version__ = '.'.join(version_info)

#here = os.path.abspath(os.path.dirname(__file__))

#v = open(os.path.join(here, 'lib', '__init__.py'))
#version = re.compile(r".*__version__ = '(.*?)'", re.S).match(v.read()).group(1)
#v.close()

#try:
#    README = open(os.path.join(here, 'README.txt')).read()
#    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
#except IOError:
#    README = CHANGES = ''

setup(
    name='amara3-xml',
    version=__version__,
    #version='3.0.2a2',
    description="Amara3 project, which offers a variety of data processing tools. This module adds the MicroXML support, and adaptation to classic XML.",
    #long_description=README + '\n\n' +  CHANGES,
    author='Uche Ogbuji',
    author_email='uche@ogbuji.net',
    url='http://uche.ogbuji.net',
    license='Apache',
    package_dir={'amara3': 'lib'},
    packages = ['amara3', 'amara3.uxml'],
    keywords = ["xml", "web", "data"],
    #scripts=['exec/exhibit_agg', 'exec/exhibit_lint'],
    classifiers = [ # From http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        #"Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
    ],
    long_description = '''
    '''
    #install_requires=[
      # -*- Extra requirements: -*-
    #    'nose',
    #    'sphinx'
    #],
)
