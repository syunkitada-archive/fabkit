# coding: utf-8

import os
import itertools
import subprocess
import sys
from fabkit import api, util
from oslo_config import generator, cfg
from oslo_messaging._drivers import amqp
from oslo_messaging._drivers import impl_rabbit
from oslo_db.options import database_opts
from oslo_log import _options
from fabkit.conf import conf_base, conf_fabric, conf_web, conf_test


list_opts = [
    ('DEFAULT',
     itertools.chain(
         conf_base.default_opts,
         conf_fabric.default_opts,
         _options.common_cli_opts,
         _options.logging_cli_opts,
     )),
    ('cluster',
     itertools.chain(
         conf_base.cluster_opts,
     )),
    ('client',
     itertools.chain(
         conf_base.client_opts,
     )),
    ('logger',
     itertools.chain(
         conf_base.logger_opts,
     )),
    ('node_logger',
     itertools.chain(
         conf_base.node_logger_opts,
     )),
    ('database',
     itertools.chain(
         database_opts,
     )),
    ('oslo_messaging_rabbit', itertools.chain(
        itertools.chain(amqp.amqp_opts, impl_rabbit.rabbit_opts))),
    ('web',
     itertools.chain(
         conf_web.web_opts,
     )),
    ('test',
     itertools.chain(
         conf_test.test_opts,
     )),
]

output_file = ''
wrap_width = 70

CONF = cfg.CONF


@api.task
def genconfig(conf_file='fabfile.ini.sample'):
    conf_file_path = os.path.join(CONF._repo_dir, conf_file)
    output_file = open(conf_file_path, 'w')
    formatter = generator._OptFormatter(output_file=output_file, wrap_width=wrap_width)

    formatter.write("#\n# fabfile.ini\n#\n")
    for section, opts in list_opts:
        formatter.write("\n\n")
        formatter.write("[{0}]\n".format(section))
        for opt in opts:
            formatter.write("\n")
            formatter.format(opt)


@api.task
def sync_fablib():
    util.git_clone_required_fablib()


@api.task
def sync_db(*args, **kwargs):
    if sys.exec_prefix == '/usr':
        subprocess.call('cd {0} && alembic upgrade head'.format(CONF._sqlalchemy_dir), shell=True)
    else:
        subprocess.call('cd {0} && {1}/bin/alembic upgrade head'.format(
            CONF._sqlalchemy_dir, sys.exec_prefix), shell=True)
