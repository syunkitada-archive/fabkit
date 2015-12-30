# coding: utf-8

from oslo_config import cfg

CONF = cfg.CONF


test_opts = [
    cfg.StrOpt('user',
               default='fabric',
               help='user for test'),
    cfg.StrOpt('password',
               default='fabric',
               help='password for test'),
]

CONF.register_opts(test_opts, group='test')


def init():
    CONF.test._dockers = [
        {
            'name': 'centos7',
            'dockerfile': 'Dockerfile_centos7',
            'sudo_group': 'wheel',
            'port': 40022,
        },
        {
            'name': 'ubuntu14',
            'dockerfile': 'Dockerfile_ubuntu14',
            'sudo_group': 'sudo',
            'port': 40122,
        },
    ]

    CONF.test._clusters = [
        'centos7/',
        'ubuntu14/',
    ]
