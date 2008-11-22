# -*- coding: utf-8 -*-
# 
# TracAlchemy - http://www.schwarz.eu/oss/
# 
# This module contains glue code to use SQLAlchemy on top trac's database
# connections. No handwritten SQL anymore!
# 
# Example:
# from tracalchemy import ORMSession
# session = ORMSession(self.env).get()
# # define your tables/mappers here
# results = session.query(MyMappedObject).filter(MyMappedObject.name=='foo')
# 
# 
# The MIT License
# 
# Copyright (c) 2008 Felix Schwarz <felix.schwarz@oss.schwarz.eu>
# 
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


from threading import RLock

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import Pool, _ConnectionRecord

from trac.core import Component



class ORMSession(Component):
    
    def __init__(self, *args, **kwargs):
        super(ORMSession, self).__init__(*args, **kwargs)
        self.engine = None
        self.engine_creation_lock = RLock()
    
    def _get_or_create_engine(self):
        self.engine_creation_lock.acquire(blocking=True)
        try:
            if self.engine == None:
                db_type = 'sqlite'
                connection_string = '%s://' % db_type
                pool = TracDatabasePool(self.env)
                engine = create_engine(connection_string, pool=pool)
                self.engine = engine
        finally:
            self.engine_creation_lock.release()
        assert self.engine != None
        return self.engine
    
    def get(self):
        engine = self._get_or_create_engine()
        Session = sessionmaker(bind=engine, autoflush=False, transactional=True)
        session = Session()
        return session



class TracDatabasePool(Pool):
    
    def __init__(self, env, **kwargs):
        self.env = env
        self.pool_lock = RLock()
        self.pooled_connections = dict()
        
        creator = self._get_connection_from_trac
        super(TracDatabasePool, self).__init__(creator, **kwargs)
        self.connection = _ConnectionRecord(self)
    
    def _get_connection_from_trac(self):
        pooled_connection = self.env.get_db_cnx()
        wrapped_db_connection = pooled_connection.cnx
        plain_dpapi_connection = wrapped_db_connection.cnx
        self.pool_lock.acquire(blocking=True)
        try:
            self.pooled_connections[plain_dpapi_connection] = pooled_connection
        finally:
            self.pool_lock.release()
        return plain_dpapi_connection
    
    def recreate(self):
        raise NotImplementedError
    
    def do_return_conn(self, conn):
        self.pool_lock.acquire(blocking=True)
        try:
            if conn in self.pooled_connections:
                print 'I know connection already!'
                pooled_connection = self.pooled_connections[conn]
                pooled_connection.close()
                del self.pooled_connections[conn]
        finally:
            self.pool_lock.release()
    
    def do_get(self):
        return self.create_connection()
    
    def status(self):
        return "TracDatabasePool"
    
    def dispose(self):
        """Close all connections in the pool"""
        raise NotImplementedError

