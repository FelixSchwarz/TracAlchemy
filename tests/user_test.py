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

from datetime import datetime as DateTime, timedelta as TimeDelta

from sqlalchemy import and_
from trac.util.datefmt import utc, to_timestamp
from trac_dev_platform.test import *

from tracalchemy.core import TracAlchemy
from tracalchemy.user import User


class UserTest(TracTest):
    def setUp(self):
        self.super()
        self.env = EnvironmentStub()
        self.session = TracAlchemy(self.env).session()
    
    def _create_user(self, username, is_authenticated=True, last_visit=None, **attributes):
        last_visit = to_timestamp(last_visit or DateTime.now(utc))
        authenticated = 1 if is_authenticated else 0
        with self.env.db_transaction as db:
            db("INSERT INTO session VALUES (%s,%s,%s)",
               (username, authenticated, last_visit))
            for key, value in attributes.items():
                db("INSERT INTO session_attribute VALUES (%s,%s,%s,%s)",
                   (username, authenticated, key, value))
    
    def test_can_use_simple_sqlalchemy_queries(self):
        yesterday = DateTime.now(utc) - TimeDelta(days=4)
        self._create_user(u'foo', last_visit=yesterday)
        self.session.commit()
        
        user = User.query(self.session).filter(and_(
            User.username == u'foo',
            User._authenticated == True,
            User.last_visit == to_timestamp(yesterday),
        )).one()
        assert_equals(u'foo', user.username)
        assert_true(user._authenticated)
        assert_equals(to_timestamp(yesterday), user.last_visit)
