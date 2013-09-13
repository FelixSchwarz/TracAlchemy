
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
