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

import alembic
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.operations import Operations
from alembic.script import ScriptDirectory

from tracalchemy.core import TracAlchemy


__all__ = ['is_upgrade_necessary', 'run_migrations']

def _script_and_context(env, db, script_location):
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", script_location)
    script = ScriptDirectory.from_config(alembic_cfg)
    
    connection = TracAlchemy(env).sqlalchemy_connection(db)
    context = MigrationContext.configure(connection, opts={'script': script})
    return (script, context)

def is_upgrade_necessary(env, db, script_location):
    script, context = _script_and_context(env, db, script_location)
    return script._current_head() != context._current_rev()
    
def run_migrations(env, db, script_location, plugin_name=''):
    def _do_log(previous_revision, revision):
        log_data = dict(old_rev=previous_revision, new_rev=revision)
        log_string = 'Upgraded ' + (plugin_name and plugin_name + ' ' or '') + \
            'database version from %(old_rev)s to %(new_rev)s'
        env.log.info(log_string % log_data)
    
    script, context = _script_and_context(env, db, script_location)
    alembic.op = Operations(context)
    current_head = script._current_head()
    current_revision = context._current_rev()
    upgrades = script.upgrade_from(current_head, current_revision, context)
    for (upgrade, previous_revision, revision) in upgrades:
        upgrade()
        context._update_current_rev(previous_revision, revision)
        db.commit()
        _do_log(previous_revision, revision)


