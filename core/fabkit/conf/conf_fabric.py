# coding: utf-8

import os
from oslo_config import cfg
from fabkit import env
from utils import complement_path

CONF = cfg.CONF

# setup fabric env
env.forward_agent = True
if os.path.isfile(os.path.expanduser(env.ssh_config_path)):
    env.use_ssh_config = True
env.warn_only = False
# env.shell = '/bin/bash -l -c'  # default
env.shell = '/bin/bash -c'
# env.sudo_prefix = "sudo -S -p '%(sudo_prompt)s' " % env  # default
env.sudo_prefix = "sudo -SE -p '%(sudo_prompt)s' "
env.colorize_errors = True
env.is_test = False
env.is_local = False
env.is_setup = False
env.is_check = False
env.is_manage = False
env.is_datamap = False


default_opts = [
    cfg.StrOpt('remote_dir',
               default='fabkit',
               help='remote_dir is storing files on remote node.'
                    'this directry is created home directry.'),
    cfg.StrOpt('user',
               default=None,
               help='user'),
    cfg.StrOpt('password',
               default=None,
               help='password'),
    cfg.StrOpt('password_file',
               default=None,
               help='password_file'),
]

CONF.register_opts(default_opts)


def init():
    if CONF.user is not None:
        env.user = CONF.user

    if CONF.password is not None:
        env.password = CONF.password
    elif CONF.password_file is not None:
        password_file = complement_path(CONF.password_file)

        if os.path.exists(password_file):
            with open(password_file, 'r') as f:
                env.password = f.read()

    CONF._remote_dir = os.path.join('/home', env.user, CONF.remote_dir)
    CONF._remote_storage_dir = os.path.join(CONF._remote_dir, 'storage')
    CONF._remote_tmp_dir = os.path.join(CONF._remote_storage_dir, 'tmp')
