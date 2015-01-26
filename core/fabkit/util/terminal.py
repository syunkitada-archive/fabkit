# coding: utf-8

from fabric import api


def confirm(msg_ask, msg_cancel=None):
    if api.env.is_test:
        return True
    if raw_input('\n%s (y/n) ' % msg_ask) == 'y':
        return True
    else:
        if msg_cancel:
            print msg_cancel
        return False
