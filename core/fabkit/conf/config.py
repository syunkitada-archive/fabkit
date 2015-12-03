# coding: utf-8

import os
from oslo_config import cfg


core_opts = [
    cfg.StrOpt('bind_host',
               default='0.0.0.0',
               help='IP address to listen on'),
]

cfg.CONF.register_opts(core_opts)


def init(repo_dir=None, test_repo_dir=None):
    cfg.CONF(args=[], default_config_files=[os.path.join(repo_dir, 'fabfile.ini')])
