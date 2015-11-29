# coding: utf-8

from oslo_config import cfg


opts = [
    cfg.StrOpt('foo'),
    cfg.StrOpt('bar'),
]

cfg.CONF.register_opts(opts, group='blaa')


def list_opts():
    return [
        ('blaa', opts),
    ]
