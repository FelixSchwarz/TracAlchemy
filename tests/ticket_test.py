# -*- coding: utf-8 -*-
# 
# Copyright (c) 2013 Felix Schwarz <felix.schwarz@oss.schwarz.eu>
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

from trac.ticket import Ticket as TracTicket

from trac_dev_platform.test import *

from tracalchemy.core import TracAlchemy
from tracalchemy.ticket import Ticket


class TicketTest(TracTest):
    def setUp(self):
        self.super()
        self.env = EnvironmentStub()
        self.session = TracAlchemy(self.env).session()
    
    def _create_trac_ticket(self, fields):
        trac_ticket = TracTicket(self.env)
        for key, value in fields.items():
            trac_ticket[key] = value
        trac_ticket.insert()
        return trac_ticket
    
    def test_can_use_simple_sqlalchemy_queries(self):
        fields = dict(
            reporter=u'foo',
            summary=u'a bug',
            description=u'I noticed failing tests.',
        )
        trac_ticket = self._create_trac_ticket(fields)
        
        ticket = Ticket.query(self.session).filter(Ticket.id == trac_ticket.id).one()
        for key, value in fields.items():
            assert_equals(value, getattr(ticket, key))
    
    def test_can_create_example_ticket(self):
        ticket = Ticket.example(_session=self.session)
        self.session.commit()
        
        assert_equals(1, ticket.id)
    
    def test_can_override_example_data(self):
        ticket = Ticket.example(_session=self.session, summary=u'help',
            description=u'some description', cc=u'foo@site.example')
        self.session.commit()
        
        assert_equals(1, ticket.id)
        assert_equals(u'help', ticket.summary)
        assert_equals(u'some description', ticket.description)
        assert_equals(u'foo@site.example', ticket.cc)
    
    def test_can_return_parsed_cc_list(self):
        ticket = Ticket.example(_session=self.session,
            cc=u'foo,bar, baz.qux; me@site.example')
        
        assert_equals(('foo', 'bar', 'baz.qux', 'me@site.example'), ticket.cc_list())
    
    def test_can_return_ticket_changes_chronologically(self):
        trac_ticket = self._create_trac_ticket(dict())
        trac_ticket['summary'] = 'new summary'
        trac_ticket.save_changes(u'foo')
        
        trac_ticket['description'] = 'describe problem'
        trac_ticket.save_changes(u'bar', u'rephrase description')
        
        ticket = Ticket.query(self.session).by_id(trac_ticket.id).one()
        assert_length(4, ticket.changes)
        
        first = ticket.changes[0]
        assert_equals(ticket, first._ticket)
        assert_equals(u'foo', first.author)
        assert_equals(u'summary', first.field)
        assert_none(first.oldvalue)
        assert_equals(u'new summary', first.newvalue)
        
        second = ticket.changes[1]
        assert_equals(ticket, second._ticket)
        assert_equals(u'foo', second.author)
        assert_equals(u'comment', second.field)
        assert_equals(u'1', second.oldvalue)
        assert_none(second.newvalue)
        
        third = ticket.changes[2]
        assert_equals(ticket, third._ticket)
        assert_equals(u'bar', third.author)
        assert_equals(u'description', third.field)
        assert_none(third.oldvalue)
        assert_equals(u'describe problem', third.newvalue)
        
        fourth = ticket.changes[3]
        assert_equals(ticket, fourth._ticket)
        assert_equals(u'bar', fourth.author)
        assert_equals(u'comment', fourth.field)
        assert_equals(u'2', fourth.oldvalue)
        assert_equals('rephrase description', fourth.newvalue)
    
    def test_can_store_custom_fields(self):
        self.create_custom_field('foo', 'text')
        
        summary = u'Ticket with custom field'
        ticket = Ticket.example(_session=self.session, summary=summary)
        ticket.custom[u'foo'] = u'bar'
        self.session.add(ticket)
        self.session.commit()
        
        trac_ticket = TracTicket(env=self.env, tkt_id=ticket.id)
        assert_equals(summary, trac_ticket['summary'])
        assert_equals('bar', trac_ticket[u'foo'])

