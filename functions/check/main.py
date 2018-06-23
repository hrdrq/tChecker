# encoding: utf-8
from __future__ import print_function, unicode_literals

import logging
import time
import json
import requests
import requests.utils
import pickle
import pyocr
import pyocr.builders
from PIL import Image
from io import BytesIO
from sqlalchemy import create_engine, func, or_, and_
from sqlalchemy.orm import sessionmaker, aliased

from utils import connect_db, JSONEncoder
from tables import TableTaaze
from credentials import *
from gmail import create_message, send_message

logger = logging.getLogger()
logger.setLevel(logging.INFO)


VALIDATE_URL = "https://www.taaze.tw/validate/validate_code.jsp"
LOGIN_URL = "https://www.taaze.tw/memberLoginValidate.html"
QUERY_URL = "http://www.taaze.tw/queryTitleMain.html"


class Taaze(object):

    def __init__(self):
        self.sql = connect_db()
        self.s = requests.Session()
        self.result = []

    def validate(self):
        res = self.s.get(VALIDATE_URL)
        img = Image.open(BytesIO(res.content))
        tools = pyocr.get_available_tools()
        if len(tools) == 0:
            print("No OCR tool found")
            sys.exit(1)
        # The tools are returned in the recommended order of usage
        tool = tools[0]
        txt = tool.image_to_string(
            img,
            lang="eng",
            builder=pyocr.builders.TextBuilder(tesseract_layout=6)
        )
        return txt

    def login(self):
        captcha = self.validate()
        self.s.post(LOGIN_URL, data={
                    'no': TAAZE_ACCOUNT, 'password': TAAZE_PW, 'validateCode': captcha})

    def query(self, isbn):
        res = self.s.get(QUERY_URL, params={"isbn": isbn}).json()[0]

        result = {
            "isbn": isbn,
            "title": res.get('titleMain'),
            "pub": res.get('pubName'),
            "flag": res.get('sndhandFlg'),  # Y:売れる
            "message": res.get('message'),
        }
        if result['flag'] == 'Y':
            self.result.append(result)
        return result


def handle(event, context):
    """
    Lambda handler
    """
    taaze = Taaze()
    taaze_rows = taaze.sql.query(TableTaaze)\
        .filter(TableTaaze.active == True)\
        .all()
    taaze.login()
    for row in taaze_rows:
        res = taaze.query(row.isbn)
        # print(json.dumps(res, indent=4, ensure_ascii=False, cls=JSONEncoder))
        logger.info(json.dumps(res, indent=4,
                               ensure_ascii=False, cls=JSONEncoder))
        if not row.title and res['title']:
            row.title = res['title']
        if not row.pub and res['pub']:
            row.pub = res['pub']
        if res['flag'] == 'B':
            row.active = False
            row.message = res['message']
        time.sleep(1)
    # print("売れる：{}".format(len(taaze.result)))
    logger.info("売れる：{}".format(len(taaze.result)))
    if taaze.result:
        subject = "{}件売れるやつがあった".format(len(taaze.result))
        # print(json.dumps(taaze.result, indent=4,
        #                  ensure_ascii=False, cls=JSONEncoder))
        logger.info(json.dumps(taaze.result, indent=4,
                               ensure_ascii=False, cls=JSONEncoder))
    else:
        subject = "売れるやつが無かった"

    body = json.dumps(taaze.result, indent=4,
                      ensure_ascii=False, cls=JSONEncoder)
    msg = create_message(GMAIL_ADDR, RECEIVE_ADDR, subject, body)
    send_message(GMAIL_ADDR, [RECEIVE_ADDR], msg)
    taaze.sql.commit()
    taaze.sql.close()
