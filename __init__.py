# coding: utf-8

import re, os, json, commands, datetime, sys
from fabric.api import env

# append library
sys.path.append(os.path.join(os.path.dirname(__file__)))
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
import conf, util
from api import *

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

fablib = conf.fablib
for name in fablib:
    lib_path = os.path.join(conf.chef_repo_path, 'fablib/%s' % name)
    if not os.path.exists(lib_path) and util.confirm('%s is not exists in fablib. git clone %s?' % (name, name)):
        print cmd('git clone %s %s' % (fablib[name], lib_path))

# import fabscirpts
sys.path.append(conf.chef_repo_path)
fabscript = os.path.join(conf.chef_repo_path, './fabscript')
if os.path.exists(fabscript):
    from fabscript import *

