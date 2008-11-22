#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup

PACKAGE = 'TracAlchemy'
VERSION = '0.1'

setup(
    name           = 'TracAlchemy',
    version        = '0.1',
    author         = 'Felix Schwarz',
    author_email   = 'felix.schwarz@oss.schwarz.eu',
    url            = 'http://www.schwarz.eu/oss/',
    description    = 'Adapter to make SQLAlchemy usable in Trac',
    license        = 'MIT',
    
    packages       = ['tracalchemy'],
    entry_points   = {'trac.plugins': ['tracalchemy = tracalchemy']},
    install_requires = ['SQLAlchemy >= 0.4']
)

