# encoding: utf-8
from __future__ import print_function, unicode_literals
import json
import decimal
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from credentials import *


class JSONEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        elif isinstance(o, unicode):
            return str(o)
        elif isinstance(o, datetime.datetime):
            return o.isoformat()

        return super(JSONEncoder, self).default(o)


def connect_db():
    ENGINE = create_engine('{dialect}+{driver}://{username}:{pwd}@{host}:{port}/{dbname}?charset=utf8'.format(
        dialect='mysql',
        driver='pymysql',
        username=DB_USERNAME,
        pwd=DB_PW,
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME
    ), echo=False)
    Session = sessionmaker(bind=ENGINE)
    # MySQLを処理するツール
    return Session()
