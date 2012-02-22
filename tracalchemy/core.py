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

import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.orm import create_session
from sqlalchemy.pool import NullPool
from trac.db.api import _parse_db_str, DatabaseManager


__all__ = ['TracAlchemy']

class DummyPool(NullPool):
    def __init__(self, tracalchemy):
        creator = lambda: tracalchemy.connection()
        super(DummyPool, self).__init__(creator)
    
    def _do_return_conn(self, _conn):
        pass
    
    def recreate(self):
        return self


class TracAlchemy(object):
    def __init__(self, env):
        self.env = env
    
    def connection(self, db=None):
        if db is None:
            db = self.env.get_db_cnx()
        conn = db
        while hasattr(conn, 'cnx'):
            conn = conn.cnx
        return conn
    
    def sqlalchemy_connection(self, db=None):
        plain_connection = self.connection(db=db)
        return Connection(self.engine(), connection=plain_connection)
    
    def sqlalchemy_connection_uri(self):
        trac_connection_uri = DatabaseManager(self.env).connection_uri
        scheme, args = _parse_db_str(trac_connection_uri)
        # TODO: Support non-sqlite DBs
        
        if scheme == 'sqlite':
            path = args['path']
            if (path != ':memory:') and (not path.startswith(os.sep)):
                path = os.path.abspath(os.path.join(self.env.path, path.strip('/')))
            # sqlalchemy needs sqlite:////path' for an absolute path
            args['path'] = '/' + path
        args['scheme'] = scheme
        return '%(scheme)s://%(path)s' % args
    
    def engine(self):
        connection_string = '%s://' % self._db_scheme()
        engine = create_engine(connection_string, pool=DummyPool(self))
        return engine
    
    def session(self):
        return create_session(self.engine(), autocommit=False)
    
    def _db_scheme(self):
        trac_connection_uri = DatabaseManager(self.env).connection_uri
        scheme, args = _parse_db_str(trac_connection_uri)
        return scheme

