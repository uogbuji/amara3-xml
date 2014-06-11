# -*- coding: utf-8 -*-
from distutils.core import setup
import sys, os

#here = os.path.abspath(os.path.dirname(__file__))

#v = open(os.path.join(here, 'lib', '__init__.py'))
#version = re.compile(r".*__version__ = '(.*?)'", re.S).match(v.read()).group(1)
#v.close()

#try:
#    README = open(os.path.join(here, 'README.txt')).read()
#    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
#except IOError:
#    README = CHANGES = ''

setup(name='amara3',
      #version=version,
      version='0.0.2',
      description="Amara processing library for MicroXML and more",
      #long_description=README + '\n\n' +  CHANGES,
      #classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      #keywords='',
      author='Uche Ogbuji',
      author_email='uche@ogbuji.net',
      url='http://uche.ogbuji.net',
      license='Apache',
      package_dir={'amara3': 'lib'},
      packages = ['amara3', 'amara3.uxml'],
      #data_files=[('amara3/uxml', ['lib/uxml/lextokens.pickle',])]
      #install_requires=[
          # -*- Extra requirements: -*-
      #    'nose',
      #    'sphinx'
      #],
      )
