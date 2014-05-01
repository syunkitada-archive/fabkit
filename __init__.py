# coding: utf-8

import re, os, json, commands, datetime, sys
from fabric.api import env

# append library
sys.path.append(os.path.join(os.path.dirname(__file__)))
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
import conf, util

# setup fabric env
env.forward_agent = True

# register tasks
from test import test
from node import node
from role import role
from prepare import prepare
from cook import cook

