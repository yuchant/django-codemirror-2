#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:       Yuji
# Last Change:  18-Mar-2011.
#
from setuptools import setup, find_packages

version = "0.1"

def read(filename):
    import os.path
    return open(os.path.join(os.path.dirname(__file__), filename)).read()
setup(
    name="django-codemirror-2",
    version=version,
    description = "",
    long_description=read('README.rst'),
    classifiers = [
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
    keywords = "django widget textarea codemirror",
    author = "Yuji Tomita",
    author_email = "lambdalisue@hashnote.net",
    url=r"https://github.com/yuchant/django-codemirror-2",
    license = 'Beerware',
    packages = find_packages(),
    package_dir = {
        'codemirror': 'codemirror',
    },
    include_package_data = True,
    zip_safe = False,
    install_requires=['setuptools'],
)
