# coding: utf-8

import os
import sys
import ConfigParser
import logging
from fabkit import api, env
from constant import (  # noqa
    INIFILE_NAME,
    STDOUT_LOG_FILE_NAME,
    ALL_LOG_FILE_NAME,
    ERROR_LOG_FILE_NAME,
    DOC_DIR_NAME,
    YAML_EXTENSION,
    CLUSTER_YAML,
    FABSCRIPT_YAML,
    DATAMAP_DIR,
)


# setup fabric env
env.forward_agent = True
env.use_ssh_config = True
env.warn_only = False
env.colorize_errors = True
env.is_test = False
env.is_setup = False
env.is_check = False
env.is_manage = False
env.is_datamap = False
env.cmd_history = []  # for debug
env.last_runs = []

env.node = {}
env.node_map = {}
env.fabscript = {}
env.fabscript_map = {}
env.cluster = {}
env.cluster_map = {}


# append module dir to sys.path
def init(fabfile_dir=None, repo_dir=None, test_repo_dir=None):
    if api.env.is_test:
        api.env.cmd_history = []  # for debug
        api.env.last_runs = []
        api.env.hosts = []
        api.env.node_map = {}

    global CONFIG
    global PARALLEL_POOL_SIZE
    global REPO_DIR, TEST_REPO_DIR
    global FABFILE_DIR, DOC_DIR
    global REMOTE_NODE, REMOTE_DIR, REMOTE_STORAGE_DIR, REMOTE_TMP_DIR
    global STORAGE_DIR, LOG_DIR, TMP_DIR, DATABAG_DIR
    global FABSCRIPT_MODULE, FABSCRIPT_MODULE_DIR, NODE_DIR, ROLE_DIR
    global FABLIB_MODULE_DIR, FABLIB_MAP
    global LOGGER_LEVEL, LOGGER_FORMATTER, LOGGER_CONSOLE_LEVEL, LOGGER_CONSOLE_FORMATTER
    global STDOUT_LOG_FILE, ALL_LOG_FILE, ERROR_LOG_FILE
    global LOGGER_MAX_BYTES, LOGGER_BACKUP_COUNT, NODE_LOGGER_MAX_BYTES, NODE_LOGGER_BACKUP_COUNT
    global WEB_LOG_LENGTH
    global USER, PASSWORD

    if fabfile_dir:
        FABFILE_DIR = fabfile_dir
        DOC_DIR = os.path.join(fabfile_dir, DOC_DIR_NAME)
    if test_repo_dir:
        TEST_REPO_DIR = test_repo_dir
    if repo_dir:
        REPO_DIR = repo_dir
    elif TEST_REPO_DIR:
        if TEST_REPO_DIR not in sys.path:
            sys.path.remove(REPO_DIR)
            sys.path.append(TEST_REPO_DIR)
        REPO_DIR = TEST_REPO_DIR

    # complement to absolute path from path relative to the fabrepo
    def complement_path(path, is_check_dir=False):
        if path == '':
            return None
        if path.find('/') == 0:
            return path
        elif path.find('~') == 0:
            return os.path.expanduser(path)

        return os.path.join(REPO_DIR, path)

    INIFILE = os.path.join(REPO_DIR, INIFILE_NAME)

    CONFIG = ConfigParser.SafeConfigParser()
    CONFIG.read(INIFILE)

    # read common settings
    api.env.pool_size = CONFIG.get('common', 'parallel_pool_size')

    #
    # LOCAL settings
    #
    STORAGE_DIR = complement_path(CONFIG.get('common', 'storage_dir'))
    TMP_DIR = os.path.join(STORAGE_DIR, 'tmp')
    LOG_DIR = os.path.join(STORAGE_DIR, 'log')
    STDOUT_LOG_FILE = os.path.join(LOG_DIR, STDOUT_LOG_FILE_NAME)

    DATABAG_DIR = complement_path(CONFIG.get('common', 'databag_dir'))
    NODE_DIR = complement_path(CONFIG.get('common', 'node_dir'))
    FABSCRIPT_MODULE = CONFIG.get('common', 'fabscript_module')
    FABSCRIPT_MODULE_DIR = os.path.join(REPO_DIR, FABSCRIPT_MODULE)
    FABLIB_MODULE = CONFIG.get('common', 'fablib_module')
    FABLIB_MODULE_DIR = os.path.join(REPO_DIR, FABLIB_MODULE)

    #
    # REMOTE settings
    #
    REMOTE_NODE = CONFIG.get('common', 'remote_node')
    REMOTE_DIR = complement_path(CONFIG.get('common', 'remote_dir'))
    REMOTE_STORAGE_DIR = os.path.join(REMOTE_DIR, 'storage')
    REMOTE_TMP_DIR = os.path.join(REMOTE_STORAGE_DIR, 'tmp')

    #
    # USER settings
    #
    USER = CONFIG.get('common', 'user')
    PASSWORD = CONFIG.get('common', 'password')
    api.env.user = USER
    api.env.password = PASSWORD

    #
    # LOGGER settings
    #
    ALL_LOG_FILE = os.path.join(LOG_DIR, ALL_LOG_FILE_NAME)
    ERROR_LOG_FILE = os.path.join(LOG_DIR, ERROR_LOG_FILE_NAME)

    LOGGER_LEVEL = getattr(logging, CONFIG.get('logger', 'level').upper())

    LOGGER_FORMAT = CONFIG.get('logger', 'format', True)
    LOGGER_FORMATTER = logging.Formatter(fmt=LOGGER_FORMAT)
    LOGGER_CONSOLE_FORMAT = CONFIG.get('logger', 'console_format', True)
    LOGGER_CONSOLE_FORMATTER = logging.Formatter(fmt=LOGGER_CONSOLE_FORMAT)

    LOGGER_CONSOLE_LEVEL = getattr(logging, CONFIG.get('logger', 'console_level').upper())

    LOGGER_MAX_BYTES = CONFIG.getint('logger', 'max_bytes')
    LOGGER_BACKUP_COUNT = CONFIG.getint('logger', 'backup_count')
    NODE_LOGGER_MAX_BYTES = CONFIG.getint('node_logger', 'max_bytes')
    NODE_LOGGER_BACKUP_COUNT = CONFIG.getint('node_logger', 'backup_count')

    #
    # WEB settings
    #
    WEB_LOG_LENGTH = CONFIG.getint('web', 'log_length')
