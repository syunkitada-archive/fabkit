# coding: utf-8

import os
import logging
from oslo_config import cfg
from oslo_log import log
from utils import complement_path
from oslo_db.options import database_opts

from constant import (  # noqa
    INIFILE_NAME,
    ALL_LOG_FILE_NAME,
    ERROR_LOG_FILE_NAME,
    DOC_DIR_NAME,
    YAML_EXTENSION,
    CLUSTER_YAML,
    CLUSTER_PICKLE,
    FABSCRIPT_YAML,
    DATAMAP_DIR,
)

CONF = cfg.CONF

default_opts = [
    cfg.StrOpt('storage_dir',
               default='storage',
               help='storage_dir is storing files(e.g. logs, packages of chef).'
                    '[absolute path or relative path from chef-repo]'),
    cfg.StrOpt('databag_dir',
               default='databag',
               help='databag dir'),
    cfg.StrOpt('filebag_dir',
               default='filebag',
               help='filebag dir'),
    cfg.StrOpt('node_dir',
               default='nodes',
               help='node dir'),
    cfg.StrOpt('handler_dir',
               default='handlers',
               help='handler dir'),
    cfg.StrOpt('fabscript_module',
               default='fabscript',
               help='fabscript_module is module including user\'s scripts of fabric.'
                    'This module must be placed in the repository.'),
    cfg.StrOpt('fablib_module',
               default='fablib',
               help='fablib_module is module including library of user or vendor for fabscript.'
                    'This module must be placed in the repository.'),
    cfg.DictOpt('fablib',
                default={},
                help='fablib_module is module including library of user or vendor for fabscript.'
                     'This module must be placed in the repository.'),
    cfg.StrOpt('dict_merge_style',
               default='nested',
               help='Merge style of cluster vars. (nested or update)'),
    cfg.IntOpt('max_recent_clusters',
               default=3,
               help='Max number of clusters save.'),
    cfg.IntOpt('retry_interval',
               default=3,
               help='Interval for retry.'),
    cfg.StrOpt('host',
               default='localhost',
               help='host'),
]

cluster_opts = [
    cfg.DictOpt('database_map',
                default={},
                help='database_map'),
]

logger_opts = [
    cfg.StrOpt('level',
               default='info',
               help='log level(debug, info, warning, error, critical)'),
    cfg.StrOpt('format',
               default='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
               help='format of log message'),
    cfg.StrOpt('console_level',
               default='info',
               help='log level(debug, info, warning, error, critical) for console output'),
    cfg.StrOpt('console_format',
               default='[%(name)s] %(levelname)s: %(message)s',
               help='format of log message for console output'),
    cfg.IntOpt('max_bytes',
               default=20000,
               help='max bytes of log file (all.log, error.log)'),
    cfg.IntOpt('backup_count',
               default=2,
               help='backup count of log file (all.log, error.log)'),
]

node_logger_opts = [
    cfg.IntOpt('max_bytes',
               default=10000,
               help='max bytes of node log file ([hostname].log)'),
    cfg.IntOpt('backup_count',
               default=0,
               help='backup count of node log file ([hostname].log)'),
]

keystone_opts = [
    cfg.StrOpt('os_auth_url',
               default='http://localhost:5000/v2.0',
               help='os_auth_url'),
    cfg.StrOpt('os_tenant_name',
               default='myfabkit',
               help='os_tenant_name'),
    cfg.StrOpt('os_username',
               default='myfabkit',
               help='os_username'),
    cfg.StrOpt('os_password',
               default='mypassword',
               help='os_password'),
]

client_opts = [
    cfg.StrOpt('endpoint',
               default='http://localhost',
               help='endpoint'),
    cfg.StrOpt('username',
               default='admin',
               help='username'),
    cfg.StrOpt('password',
               default='admin',
               help='password'),
    cfg.StrOpt('group',
               default='admin',
               help='group'),
    cfg.ListOpt('clusters',
                default=[],
                help='clusters'),
    cfg.ListOpt('setup_task_patterns',
                default=['local.*', 'check.*'],
                help='setup_task_patterns'),
    cfg.StrOpt('package_prefix',
               default='/opt/fabkit',
               help='package_prefix'),
    cfg.StrOpt('package_var_dir',
               default='/var/lib/fabkit',
               help='package_var_dir'),
]

agent_opts = [
    cfg.IntOpt('agent_report_interval',
               default=60,
               help='report_interval'),
    cfg.IntOpt('agent_downtime',
               default=120,
               help='agent_downtime'),
    cfg.IntOpt('check_task_interval',
               default=60,
               help='check_task_interval'),
    cfg.IntOpt('check_event_interval',
               default=60,
               help='check_event_interval'),
    cfg.IntOpt('delete_event_interval',
               default=180,
               help='delete_event_interval'),
]

network_opts = [
    cfg.StrOpt('libvirt_net',
               default='br-local:172.16.100.0/24',
               help='libvirt_net'),
    cfg.StrOpt('domain',
               default='example.com',
               help='hostname suffix domain'),
]


CONF.register_opts(default_opts)
CONF.register_opts(cluster_opts, group='cluster')
CONF.register_opts(keystone_opts, group='keystone')
CONF.register_opts(logger_opts, group='logger')
CONF.register_opts(node_logger_opts, group='node_logger')
CONF.register_opts(client_opts, group='client')
CONF.register_opts(agent_opts, group='agent')
CONF.register_opts(database_opts, group='database')
CONF.register_opts(database_opts, group='pdns_database')
CONF.register_opts(network_opts, group='network')


def init(repo_dir=None, log_file=None):
    INIFILE = os.path.join(repo_dir, INIFILE_NAME)
    log.register_options(CONF)
    if os.path.exists(INIFILE):
        CONF([], default_config_files=[INIFILE])
    else:
        CONF([])

    CONF._inifile = INIFILE
    CONF._repo_dir = repo_dir
    CONF._fabfile_dir = os.path.join(repo_dir, 'fabfile')
    CONF._conf_dir = os.path.join(repo_dir, 'conf')
    CONF._sqlalchemy_dir = os.path.join(CONF._fabfile_dir, 'core', 'db', 'impl_sqlalchemy')
    CONF._pdns_sqlalchemy_dir = os.path.join(CONF._fabfile_dir, 'core', 'pdns', 'impl_sqlalchemy')
    CONF._webapp_dir = os.path.join(CONF._fabfile_dir, 'core', 'webapp')
    CONF._storage_dir = complement_path(CONF.storage_dir)
    CONF._webapp_storage_dir = os.path.join(CONF._storage_dir, 'webapp')
    CONF._handler_dir = complement_path(CONF.handler_dir)
    CONF._databag_dir = complement_path(CONF.databag_dir)
    CONF._filebag_dir = complement_path(CONF.filebag_dir)
    CONF._tmp_dir = os.path.join(CONF._storage_dir, 'tmp')
    CONF._log_dir = os.path.join(CONF._storage_dir, 'log')
    CONF._node_dir = complement_path(CONF.node_dir)
    CONF._job_yml = os.path.join(CONF._conf_dir, 'job.yml')
    CONF._fabscript_module_dir = complement_path(CONF.fabscript_module)
    CONF._fablib_module_dir = complement_path(CONF.fablib_module)
    CONF._node_meta_pickle = os.path.join(CONF._node_dir, 'meta.pickle')

    CONF._all_log_file_name = ALL_LOG_FILE_NAME
    CONF._error_log_file_name = ERROR_LOG_FILE_NAME
    CONF._fabscript_yaml = FABSCRIPT_YAML
    CONF._yaml_extension = YAML_EXTENSION
    CONF._cluster_yaml = CLUSTER_YAML
    CONF._cluster_pickle = CLUSTER_PICKLE
    CONF._datamap_dir = DATAMAP_DIR

    CONF._logger_formatter = logging.Formatter(fmt=CONF.logger.format)
    CONF._logger_console_formatter = logging.Formatter(fmt=CONF.logger.console_format)

    CONF._check_agent_interval = CONF.agent.agent_downtime // 2

    if log_file is None:
        log.setup(CONF, 'fabkit')
    else:
        CONF.log_file = os.path.join(CONF.log_dir, log_file)
        log.setup(CONF, 'fabkit')
