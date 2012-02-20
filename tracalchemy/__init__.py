# -*- coding: utf-8 -*-
# 
# TracAlchemy - http://www.schwarz.eu/oss/
# 
# Glue code to use SQLAlchemy on top Trac's database connections. 
# No handwritten SQL anymore!
# 
# Example:
# >>> from tracalchemy import TracAlchemy
# >>> session = TracAlchemy(self.env).session()
# # define your tables/mappers here
# >>> results = session.query(MyMappedObject).filter(MyMappedObject.name=='foo')

from tracalchemy.session import *


