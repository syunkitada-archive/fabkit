# coding: utf-8

import os
import itertools
import commands
from fabkit import api, util
from oslo_config import generator, cfg
from oslo_log import _options
from fabkit.conf import conf_base, conf_fabric, conf_web, conf_test
from swiftclient.service import SwiftService, SwiftUploadObject


list_opts = [
    ('DEFAULT',
     itertools.chain(
         conf_base.default_opts,
         conf_fabric.default_opts,
         _options.common_cli_opts,
         _options.logging_cli_opts,
     )),
    ('keystone',
     itertools.chain(
         conf_base.keystone_opts,
     )),
    ('logger',
     itertools.chain(
         conf_base.logger_opts,
     )),
    ('node_logger',
     itertools.chain(
         conf_base.node_logger_opts,
     )),
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
def upload():
    print dict(CONF.keystone)
    container = 'fabkit'
    with SwiftService(options=dict(CONF.keystone)) as swift:
        status, output = commands.getstatusoutput(
            'rm -rf /tmp/fabkit-repo && '
            'cp -r {0} /tmp/fabkit-repo && '
            'rm -rf /tmp/fabkit-repo/fabfile/core/webapp && '
            'rm -rf /tmp/fabkit-repo/storage/tmp && '
            'find /tmp/fabkit-repo -name .git | xargs rm -rf && '
            'find /tmp/fabkit-repo -name .tox | xargs rm -rf && '
            'find /tmp/fabkit-repo -name test-repo | xargs rm -rf && '
            'find /tmp/fabkit-repo -name *.pyc | xargs rm -rf && '
            'cd /tmp/ && tar cf fabkit-repo.tar.gz fabkit-repo'.format(CONF._repo_dir))

        objs = [
            SwiftUploadObject('/tmp/fabkit-repo.tar.gz', 'fabkit-repo.tar.gz')
        ]

        for r in swift.upload(container, objs):
            print r


@api.task
def client():
    container = 'fabkit'
    with SwiftService(options=dict(CONF.keystone)) as swift:
        options = {
            'out_directory': '/opt/fabkit/var/',
        }
        for r in swift.download(container, ['fabkit-repo.tar.gz'], options=options):
            print r

    # TODO setup:local
