# coding: utf-8

from oslo_config import cfg

CONF = cfg.CONF


web_opts = [
    cfg.StrOpt('hostname',
               default='localhost',
               help='Hostname of webserver.'),
    cfg.IntOpt('port',
               default=8080,
               help='Port of webserver.'),
    cfg.BoolOpt('is_https',
                default=False,
                help='Wheter to use HTTPS'),
    cfg.BoolOpt('debug',
                default=True,
                help='Debug'),
    cfg.StrOpt('secret_key',
               default='CHANGE_ME',
               help='SECRET_KEY of Django'),
    cfg.StrOpt('language_code',
               default='ja',
               help='LANGUAGE_CODE of Django'),
    cfg.StrOpt('time_zone',
               default='Asia/Tokyo',
               help='TIME_ZONE of Django'),
    cfg.ListOpt('nodes',
                default=[],
                help='nodes of Nodejs.\n'
                'nodes = http://localhost:4000, http://localhost:4001'),
]

CONF.register_opts(web_opts, group='web')
