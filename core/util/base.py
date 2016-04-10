# coding: utf-8

import os
import itertools
import commands
import subprocess
from fabkit import api, util
from oslo_config import generator, cfg
from oslo_messaging._drivers import amqp
from oslo_messaging._drivers import impl_rabbit
from oslo_db.options import database_opts
from oslo_log import _options
from fabkit.conf import conf_base, conf_fabric, conf_web, conf_test
from swiftclient.service import SwiftService, SwiftUploadObject, SwiftError


list_opts = [
    ('DEFAULT',
     itertools.chain(
         conf_base.default_opts,
         conf_fabric.default_opts,
         _options.common_cli_opts,
         _options.logging_cli_opts,
     )),
    ('client',
     itertools.chain(
         conf_base.client_opts,
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
def upload():
    print dict(CONF.keystone)
    container = 'fabkit'
    with SwiftService(options=dict(CONF.keystone)) as swift:
        try:
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
                if r['success']:
                    if 'object' in r:
                        print(r['object'])
                    elif 'for_object' in r:
                        print(
                            '%s segment %s' % (r['for_object'],
                                               r['segment_index'])
                            )
                else:
                    error = r['error']
                    if r['action'] == "create_container":
                        print(
                            'Warning: failed to create container '
                            "'%s'", container
                        )
                    elif r['action'] == "upload_object":
                        print(
                            "Failed to upload object %s to container %s: %s" %
                            (container, r['object'], error)
                        )
                    else:
                        print("%s" % error)

        except SwiftError as e:
            print(e.value)


@api.task
def client():
    container = 'fabkit'
    with SwiftService(options=dict(CONF.keystone)) as swift:
        options = {
            'out_directory': '/opt/fabkit/var/',
        }
        for r in swift.download(container, ['fabkit-repo.tar.gz'], options=options):
            print r

    status, output = commands.getstatusoutput(
        'cd /opt/fabkit/var && rm -rf fabkit-repo && tar xf fabkit-repo.tar.gz')

    status, output = commands.getstatusoutput(
        'cp {0} /opt/fabkit/var/fabkit-repo'.format(CONF._inifile))

    for cluster in CONF.client.clusters:
        print cluster
        node = os.path.join(cluster, CONF.client.host)
        for task in CONF.client.task_patterns:
            status, output = commands.getstatusoutput(
                '/opt/fabkit/bin/fab -f /opt/fabkit/var/fabkit-repo/fabfile '
                'node:{0},local manage:{1}'.format(node, task))
            print output


@api.task
def sync_db(*args, **kwargs):
    subprocess.call('cd {0} && alembic upgrade head'.format(CONF._sqlalchemy_dir), shell=True)
