# coding: utf-8

import datetime


def get_timestamp():
    today = datetime.datetime.today()
    return today.strftime('%Y-%m-%d %H:%M:%S')
