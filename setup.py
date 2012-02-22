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
    extras_require = {
        'alembic': ['alembic>=0.2'],
    },
    
    packages       = ['tracalchemy'],
    entry_points   = {
        'trac.plugins': [
            # using two separate 'trac plugins' so that 'alembic' is no hard
            # dependency
            'tracalchemy = tracalchemy',
            'traclembic = tracalchemy.migration'
        ],
        'console_scripts': ['traclembic = tracalchemy.migration.traclembic:run']
    },
)

