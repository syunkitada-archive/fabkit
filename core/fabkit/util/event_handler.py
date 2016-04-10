# coding: utf-8

import os
import re
from oslo_config import cfg

CONF = cfg.CONF
RE_PYTHON = re.compile('^(.*)\.py$')
handlers = []


def init():
    for root, dirs, files in os.walk(CONF._handler_dir):
        for file in files:
            m = RE_PYTHON.search(file)
            if m is not None:
                if m.group(0) == '__init__.py':
                    continue

                script = '.'.join([CONF.handler_dir, m.group(1)])
                module = __import__(script, globals(), locals(), ['*'], -1)
                if hasattr(module, 'hook'):
                    handlers.append(module)


def hook(event):
    for handler in handlers:
        handler.hook(event)
