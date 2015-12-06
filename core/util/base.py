# coding: utf-8

from fabkit import api
from oslo_config import cfg, generator


core_opts = [
    cfg.StrOpt('bind_host',
               default='0.0.0.0',
               help='IP address to listen on'),
]


cfg.CONF.register_opts(core_opts)


@api.task
def genconfig():
    print 'test'
    generator.generate(cfg.CONF)
