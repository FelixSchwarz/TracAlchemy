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

import re

from sqlalchemy import BigInteger, Integer, String, UnicodeText
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapper, relationship, Query
from sqlalchemy.schema import (Column, ForeignKey, Index, MetaData,
    PrimaryKeyConstraint, Table)


__all__ = ['Ticket']


metadata = MetaData()
Base = declarative_base()

ticket_table = Table('ticket', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('type', String),
    Column('time', BigInteger, server_default=None),
    Column('changetime', BigInteger, server_default=None),
    
    Column('component', String),
    Column('severity', String),
    Column('priority', String),
    Column('owner', String),
    Column('reporter', String),
    Column('cc', String),
    Column('version', String),
    Column('milestone', String),
    Column('status', String),
    Column('resolution', String),
    Column('summary', String),
    Column('description', String),
    Column('keywords', String),
    
    Index('ticket_time_idx', 'time'),
    Index('ticket_status_idx', 'status'),
)


class TicketQuery(Query):
    def by_id(self, ticket_id):
        return self.filter(Ticket.id == ticket_id)

class Ticket(object):
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
    
    def cc_list(self):
        # --- copied from trac.web.Chrome -------------------------------------
        ccs = []
        for cc in re.split(r'[;,]', self.cc):
            cc = cc.strip()
            if cc:
                ccs.append(cc)
        return tuple(ccs)
        # --- end of copy -----------------------------------------------------


mapper(Ticket, ticket_table)

# -----------------------------------------------------------------------------

ticket_change_table = Table('ticket_change', metadata,
    Column('ticket', Integer, ForeignKey('ticket.id'), nullable=False),
    Column('time', BigInteger, nullable=False),
    Column('author', UnicodeText),
    Column('field', UnicodeText, nullable=False),
    Column('oldvalue', UnicodeText),
    Column('newvalue', UnicodeText),
    
    PrimaryKeyConstraint('ticket', 'time', 'field'),
    Index('ticket_change_ticket_idx', 'ticket'),
    Index('ticket_change_time_idx', 'time'),
)

class TicketChange(object):
    pass


mapper(TicketChange, ticket_change_table,
    properties={
        'ticket_id': ticket_change_table.c.ticket,
        '_ticket': relationship(Ticket,
            primaryjoin=(Ticket.id==ticket_change_table.c.ticket),
            backref='changes'),
    },
)

