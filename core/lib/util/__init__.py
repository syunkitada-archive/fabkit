# coding: utf-8
from fabric.api import env
# import json
import datetime
from lib.api import *  # noqa
from host import *  # noqa
from node import *  # noqa


def get_timestamp():
    today = datetime.datetime.today()
    return today.strftime('%Y-%m-%d %H:%M:%S')


def confirm(msg_ask, msg_cancel=None):
    if env.is_test:
        return True
    if raw_input('\n%s (y/n) ' % msg_ask) == 'y':
        return True
    else:
        if msg_cancel:
            print msg_cancel
        return False


def get_data_bag(bagname, itemname):
    if env.is_chef:
        result = cmd('knife data bag show %s %s -F json' % (bagname, itemname), True)
    else:
        result = cmd('knife solo data bag show %s %s -F json' % (bagname, itemname), True)
    if result[0] == 0:
        data_bag = json.loads(result[1])
        return data_bag
    else:
        return None
