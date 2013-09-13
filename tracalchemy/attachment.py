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

from sqlalchemy import BigInteger, Integer, UnicodeText
from sqlalchemy.orm import mapper
from sqlalchemy.schema import Column, Table

from tracalchemy.model_util import metadata


__all__ = ['Attachment']

attachment_table = Table('attachment', metadata,
    Column('type', UnicodeText, primary_key=True),
    Column('id', UnicodeText, primary_key=True),
    Column('filename', UnicodeText, primary_key=True),
    Column('size', Integer),
    Column('time', BigInteger),
    Column('description', UnicodeText),
    Column('author', UnicodeText),
    Column('ipnr', UnicodeText),
)


class Attachment(object):
    @classmethod
    def query(cls, session):
        return session.query(cls)


mapper(Attachment, attachment_table)

