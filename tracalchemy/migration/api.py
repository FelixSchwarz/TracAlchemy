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

from trac.core import Component, ExtensionPoint, implements, Interface
from trac.env import IEnvironmentSetupParticipant

from tracalchemy.migration.core import is_upgrade_necessary, run_migrations

__all__ = ['AlembicMigrator', 'IAlembicUpgradeParticipant']


class IAlembicUpgradeParticipant(Interface):
    def script_location(self):
        """Return the path to the directory which holds the upgrade files in a
        directory named 'versions'
        """


class AlembicMigrator(Component):
    implements(IEnvironmentSetupParticipant)
    
    plugins = ExtensionPoint(IAlembicUpgradeParticipant)
    disable_upgrade_check = False
    
    def environment_created(self):
        raise NotImplementedError()
    
    def environment_needs_upgrade(self, db):
        if self.disable_upgrade_check:
            return False
        for plugin in self.plugins:
            if is_upgrade_necessary(self.env, db, plugin.script_location()):
                return True
        return False
    
    def upgrade_environment(self, db):
        for plugin in self.plugins:
            run_migrations(self.env, db, plugin.script_location())


