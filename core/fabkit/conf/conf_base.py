# coding: utf-8

import os
import logging
from oslo_config import cfg
from oslo_log import log

from constant import (  # noqa
    INIFILE_NAME,
    STDOUT_LOG_FILE_NAME,
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
    cfg.StrOpt('node_dir',
               default='nodes',
               help='node dir'),
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


CONF.register_opts(default_opts)
CONF.register_opts(logger_opts, group='logger')
CONF.register_opts(node_logger_opts, group='node_logger')


def complement_path(path):
    if path == '':
        return None
    if path.find('/') == 0:
        return path
    elif path.find('~') == 0:
        return os.path.expanduser(path)

    return os.path.join(CONF._repo_dir, path)


def init(fabfile_dir=None, repo_dir=None):
    INIFILE = os.path.join(repo_dir, INIFILE_NAME)
    log.register_options(CONF)
    if os.path.exists(INIFILE):
        CONF([], default_config_files=[INIFILE])
    else:
        CONF([])

    CONF._fabfile_dir = fabfile_dir
    CONF._repo_dir = repo_dir
    CONF._storage_dir = complement_path(CONF.storage_dir)
    CONF._databag_dir = complement_path(CONF.databag_dir)
    CONF._tmp_dir = os.path.join(CONF._storage_dir, 'tmp')
    CONF._log_dir = os.path.join(CONF._storage_dir, 'log')
    CONF._node_dir = complement_path(CONF.node_dir)
    CONF._fabscript_module_dir = complement_path(CONF.fabscript_module)
    CONF._fablib_module_dir = complement_path(CONF.fablib_module)
    CONF._node_meta_pickle = os.path.join(CONF._node_dir, 'meta.pickle')
    CONF._all_log_file_name = ALL_LOG_FILE_NAME
    CONF._error_log_file_name = ERROR_LOG_FILE_NAME
    CONF._stdout_log_file_name = STDOUT_LOG_FILE_NAME
    CONF._fabscript_yaml = FABSCRIPT_YAML
    CONF._yaml_extension = YAML_EXTENSION
    CONF._cluster_yaml = CLUSTER_YAML
    CONF._cluster_pickle = CLUSTER_PICKLE
    CONF._datamap_dir = DATAMAP_DIR

    CONF._logger_formatter = logging.Formatter(fmt=CONF.logger.format)
    CONF._logger_console_formatter = logging.Formatter(fmt=CONF.logger.console_format)

    log.setup(CONF, 'fabkit')