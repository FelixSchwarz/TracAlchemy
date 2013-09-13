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

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Query


__all__ = ['Ticket']


Base = declarative_base()

class TicketQuery(Query):
    pass


class Ticket(Base):
    __tablename__ = 'ticket'
    
    id = Column(Integer, primary_key=True)
    type = Column(String)
    time = Column(Integer)
    changetime = Column(Integer)
    component = Column(String)
    severity = Column(String)
    priority = Column(String)
    owner = Column(String)
    reporter = Column(String)
    cc = Column(String)
    version = Column(String)
    milestone = Column(String)
    status = Column(String)
    resolution = Column(String)
    summary = Column(String)
    description = Column(String)
    keywords = Column(String)
    
    @classmethod
    def query(cls, session):
        return TicketQuery([cls], session=session)
    
    @classmethod
    def example(cls, _session=None, **kwargs):
        # Regular users should not need to install the TracDevPlatform plugin
        # so we must not put the import in the file header.
        # This method is only intended for testing so I guess it's ok to depend
        # on pythonic_testcase here.
        from trac_dev_platform.test.lib.pythonic_testcase import (assert_true,
            assert_is_empty)
        ticket = Ticket()
        for key in tuple(kwargs):
            assert_true(hasattr(ticket, key), message='Unknown attribute %r' % key)
            setattr(ticket, key, kwargs.pop(key))
        assert_is_empty(kwargs)
        if _session:
            _session.add(ticket)
        return ticket
    
    def __repr__(self):
        columns = list(Ticket.__mapper__.columns)
        settings = map(lambda column: column.name + '=' + repr(getattr(self, column.name)), columns)
        return 'Ticket(%s)' % ', '.join(settings)


