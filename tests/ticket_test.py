
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

