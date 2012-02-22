#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup

setup(
    name           = 'TracAlchemy',
    version        = '0.2dev',
    author         = 'Felix Schwarz',
    author_email   = 'felix.schwarz@oss.schwarz.eu',
    url            = 'http://www.schwarz.eu/oss/',
    description    = 'Adapter to make SQLAlchemy usable in Trac',
    license        = 'MIT',
    
    install_requires = ['SQLAlchemy >= 0.4'],
    
    packages       = ['tracalchemy'],
    entry_points   = {
        'trac.plugins': [
            'tracalchemy = tracalchemy',
        ],
    },
)

