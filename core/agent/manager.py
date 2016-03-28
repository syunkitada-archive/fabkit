# coding: utf-8

from oslo_config import cfg
from central import CentralAPI

CONF = cfg.CONF


def manage(*args, **kwargs):
    print args
    print kwargs
    if 'setup' in args:
        centralapi = CentralAPI()
        result = centralapi.setup()
        print result
