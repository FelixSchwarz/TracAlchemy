# -*- coding: utf-8 -*-
# 
# Copyright (c) 2012-2013 Felix Schwarz <felix.schwarz@oss.schwarz.eu>
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

from sqlalchemy import Integer, UnicodeText
from sqlalchemy.orm import mapper
from sqlalchemy.schema import Column, ForeignKey, Index, Table

from tracalchemy.model_util import metadata


__all__ = ['User', 'UserAttribute']


session_attribute_table = Table('session_attribute', metadata,
    Column('sid', UnicodeText, ForeignKey('session.sid'), primary_key=True),
    Column('authenticated', Integer, primary_key=True),
    Column('name', UnicodeText, primary_key=True),
    Column('value', UnicodeText),
)

class UserAttribute(object):
    @classmethod
    def query(cls, session):
        return session.query(cls)
mapper(UserAttribute, session_attribute_table)


session_table = Table('session', metadata,
    Column('sid', UnicodeText, primary_key=True),
    Column('authenticated', Integer, primary_key=True),
    Column('last_visit', Integer),
    
    Index('session_authenticated_idx', 'authenticated'),
    Index('session_last_visit_idx', 'last_visit'),
)

class User(object):
    @classmethod
    def query(cls, session):
        return session.query(cls)


mapper(User, session_table,
    properties={
        'username': session_table.c.sid,
        '_authenticated': session_table.c.authenticated,
    },
)


