# coding: utf-8

from oslo_config import cfg

CONF = cfg.CONF


web_opts = [
    cfg.IntOpt('port',
               default=8080,
               help='httpd port. this option referenced from fabnode.'),
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
    cfg.StrOpt('node_public_host',
               default='localhost',
               help='node host that web client access.'),
    cfg.IntOpt('node_public_port',
               default=4000,
               help='node port that web client access.'),
    cfg.IntOpt('node_port',
               default=4000,
               help='node port. this option referenced from fabnode.'),
    cfg.ListOpt('nodes',
                default=[],
                help='nodes of nodejs cluster. this option referenced from fabnode.\n'
                'nodes = http://localhost:4000, http://localhost:4001'),
]

CONF.register_opts(web_opts, group='web')
