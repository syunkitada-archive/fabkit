# coding: utf-8

import re, os, json, commands, datetime, sys
from fabric.api import env

# append library
sys.path.append(os.path.join(os.path.dirname(__file__)))
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
import conf, util

# setup fabric env
env.forward_agent = True
env.cmd_history = [] # for debug

# register tasks
from test import test
from node import node
from role import role
from prepare import prepare
from cook import cook
from check import check

# import fabscirpts
sys.path.append(conf.chef_repo_path)
fabscript = os.path.join(conf.chef_repo_path, './fabscript')
if os.path.exists(fabscript):
    from fabscript import *

