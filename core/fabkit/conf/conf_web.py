# coding: utf-8

from oslo_config import cfg

CONF = cfg.CONF


web_opts = [
    cfg.StrOpt('my_host',
               default='localhost',
               help='Hostname of webserver.'),
    cfg.IntOpt('port',
               default=8080,
               help='Port of webserver.'),
    cfg.BoolOpt('is_https',
                default=False,
                help='Wheter to use HTTPS'),
]

CONF.register_opts(web_opts, group='web')
