# cording: utf-8

import os
from fabkit import task, Service, Package, filer, sudo
from oslo_config import cfg

CONF = cfg.CONF


@task
def setup():
    Package('docker.io').install()
    Service('docker').start()

    for docker in CONF.test._dockers:
        data = {
            'user': CONF.test.user,
            'password': CONF.test.password,
            'sudo_group': docker['sudo_group'],
        }

        filer.template(src=docker['dockerfile'], dest=os.path.join('/tmp', docker['dockerfile']),
                       data=data)
        sudo('docker images | grep {0} ||'
             ' docker build -f /tmp/{1} -t {0} /tmp/'.format(docker['name'], docker['dockerfile']))
        sudo('docker ps | grep {0} ||'
             ' docker run -i -d -p {1}:22 {0} /usr/sbin/sshd -D'.format(
                 docker['name'], docker['port']))
