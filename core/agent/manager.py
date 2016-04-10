# coding: utf-8

import central
from oslo_config import cfg

CONF = cfg.CONF


def manage(*args, **kwargs):
    if 'help' in args:
        print 'help'

    elif 'setup' in args:
        centralapi = central.CentralAPI()
        result = centralapi.setup()
        print result

    elif 'agent-list' in args:
        pass
