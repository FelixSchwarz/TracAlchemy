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

from datetime import datetime as DateTime

from sqlalchemy import and_
from trac.attachment import Attachment as TracAttachment
from trac.util.datefmt import to_utimestamp, utc
from trac_dev_platform.test import *

from tracalchemy.core import TracAlchemy
from tracalchemy.ticket import Ticket
from tracalchemy.attachment import Attachment


class AttachmentTest(TracTest):
    def setUp(self):
        self.super()
        self.env = EnvironmentStub()
        self.session = TracAlchemy(self.env).session()
    
    def _create_trac_attachment(self, parent_id):
        description = None
        author = None
        ipnr = None
        when = DateTime.now(utc)
        with self.env.db_transaction as db:
            db("INSERT INTO attachment VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
               ('ticket', parent_id, 'foo.txt', 12345,
                to_utimestamp(when), description, author, ipnr))
        trac_attachment = TracAttachment(self.env, u'ticket',
            filename=u'foo.txt', parent_id=parent_id)
        return trac_attachment
    
    def test_can_use_simple_sqlalchemy_queries(self):
        ticket = Ticket.example(self.session)
        self.session.commit()
        trac_attachment = self._create_trac_attachment(parent_id=ticket.id)
        
        attachment = Attachment.query(self.session).filter(and_(
            Attachment.type == trac_attachment.parent_realm,
            Attachment.id == trac_attachment.parent_id,
            Attachment.filename == trac_attachment.filename,
        )).one()
        assert_equals(u'ticket', attachment.type)
        assert_equals(u'foo.txt', attachment.filename)
        assert_equals(12345, attachment.size)
        assert_equals(None, attachment.description)
        assert_equals(None, attachment.author)
        assert_equals(None, attachment.ipnr)
