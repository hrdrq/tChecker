# encoding: utf-8
from __future__ import print_function, unicode_literals
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Boolean, Column, create_engine, Integer, MetaData, String, Table, ForeignKey, text
)
from sqlalchemy.dialects.mysql import *
from sqlalchemy.orm import relation, relationship
Base = declarative_base()


class TableTaaze(Base):
    __tablename__ = 'taaze'
    id = Column(INTEGER(11, unsigned=True),
                primary_key=True, autoincrement=True)
    isbn = Column(String)
    active = Column(BOOLEAN, default=None)
    title = Column(String)
    pub = Column(String)
    message = Column(String)
