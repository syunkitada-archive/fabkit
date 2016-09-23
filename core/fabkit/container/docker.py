# cording: utf-8

import os
from fabkit import filer, sudo
from oslo_config import cfg
from fablib.base import SimpleBase

CONF = cfg.CONF


class Docker(SimpleBase):
    def __init__(self):
        self.data_key = 'test_bootstrap'
        self.packages = {
            'Ubuntu 14.*': [
                'docker.io',
            ],
            'CentOS Linux 7.*': [
                'docker-io',
            ]
        }
        self.services = [
            'docker',
        ]

    def setup(self):
        data = self.init()
        self.install_packages()
        self.start_services()

        is_updated = filer.template(src='docker.j2', dest='/etc/default/docker')
        if is_updated:
            self.restart_services()

        for docker in data['dockers']:
            data = {
                'user': CONF.test.user,
                'password': CONF.test.password,
                'docker': docker,
            }

            filer.template(src=docker['template'], dest=os.path.join('/tmp', docker['template']),
                           data=data)
            sudo('docker images | grep {0} ||'
                 ' docker build -f /tmp/{1} -t {0} /tmp/'.format(
                     docker['name'], docker['template']))

            port_option = ''
            for port in docker['ports']:
                port_option += ' -p {0[1]}:{0[0]}'.format(port)

            if docker.get('use_systemd', False):
                sudo('docker ps | grep {0} || ('
                     ' docker run --privileged -di --name {0} {1} {0} /sbin/init &&'
                     ' docker exec -di {0} /usr/sbin/sshd -D )'.format(docker['name'], port_option))
            else:
                sudo('docker ps | grep {0} || ('
                     ' docker run --privileged -di --name {0} {1} {0} /usr/sbin/sshd -D )'.format(
                         docker['name'], port_option))
