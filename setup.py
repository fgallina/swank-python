#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup

setup(name='swank-python',
      version='0.1',
      description='Swank server for Python.',
      long_description='This is a work in progress...',
      author='Fabián Ezequiel Gallina',
      author_email='fabian@anue.biz',
      maintainer='Fabián Ezequiel Gallina',
      maintainer_email='fabian@anue.biz',
      url='https://github.com/fgallina/swank-python',
      packages=['swank'],
      # package_data={'swank': ['elisp/*.el']},
      # include_package_data = True,
      requires=[],
      download_url='https://github.com/fgallina/swank-python',
      classifiers=['Intended Audience :: Developers',
                   'License :: OSI Approved :: GPL v3'],
      license='GPL v3')
