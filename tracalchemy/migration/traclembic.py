# -*- coding: utf-8 -*-
# 
# Copyright (c) 2012 Felix Schwarz <felix.schwarz@oss.schwarz.eu>
#
# The MIT License
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import os
import sys
import tempfile

from alembic import context
from alembic import config as alembic_config
from alembic.script import ScriptDirectory
from trac.env import open_environment

from tracalchemy.migration.api import AlembicMigrator
from tracalchemy.core import TracAlchemy


__all__ = ['run_traclembic']

def online_migration(engine):
    connection = engine.connect()
    context.configure(connection=connection)
    with context.begin_transaction():
        context.run_migrations()
    connection.close()

def run():
    def _open_environment(argv):
        if len(argv) < 2:
            print 'usage: %s </path/to/trac/env> [alembic options]' % argv[0]
            sys.exit(2)
        return open_environment(argv[1])
    
    def _temporary_alembic_config(env, script_location):
        alembic_ini = tempfile.NamedTemporaryFile()
        alembic_ini.write('[alembic]\n' + \
            'script_location = %s\n' % script_location + \
            'sqlalchemy.url = %s\n' % TracAlchemy(env).sqlalchemy_connection_uri())
        alembic_ini.flush()
        return alembic_ini

    argv = sys.argv
    AlembicMigrator.disable_upgrade_check = True
    env = _open_environment(argv)
    
    # monkey patch so we don't need the 'env.py' file
    engine = TracAlchemy(env).engine()
    ScriptDirectory.run_env = lambda self: online_migration(engine)
    
    plugins = AlembicMigrator(env).plugins
    if len(plugins) == 0:
        return
    # TODO: support more than one alembic plugin by changing the table name
    plugin = plugins[0]
    
    alembic_ini = _temporary_alembic_config(env, plugin.script_location())
    alembic_arguments = ['--config='+alembic_ini.name] + argv[2:]
    alembic_config.main(alembic_arguments)


