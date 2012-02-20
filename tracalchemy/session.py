# -*- coding: utf-8 -*-
# 
# Copyright (c) 2008-2012 Felix Schwarz <felix.schwarz@oss.schwarz.eu>
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


from sqlalchemy import create_engine
from sqlalchemy.orm import create_session
from sqlalchemy.pool import NullPool
from trac.core import Component

__all__ = ['TracAlchemy']

class DummyPool(NullPool):
    def __init__(self, env):
        self.env = env
        creator = lambda: self.env.get_db_cnx().cnx.cnx
        super(DummyPool, self).__init__(creator)


class TracAlchemy(Component):
    def engine(self):
        db_type = 'sqlite'
        connection_string = '%s://' % db_type
        return create_engine(connection_string, pool=DummyPool(self.env))
    
    def session(self):
        return create_session(self.engine(), autocommit=False)


