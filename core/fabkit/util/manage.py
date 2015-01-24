# coding: utf-8

from fabkit import conf, api
from terminal import confirm
import os
import commands
import logging
from logging.handlers import RotatingFileHandler


# create directory, if directory not exists
def create_dir(directory, is_create_init_py=False):
    if not os.path.exists(directory):
        if confirm('"{0}" is not exists.\nDo you want to create?'.format(directory),
                   'Canceled.') or api.env.is_test:
            os.makedirs(directory)
            print '"{0}" is created.'.format(directory)
            if is_create_init_py:
                init_py = os.path.join(directory, '__init__.py')
                with open(init_py, 'w') as f:
                    f.write('# coding: utf-8')
                    print '"{0} is created."'.format(init_py)
        else:
            exit(0)


def git_clone_required_fablib():
    for fablib_name in conf.CONFIG.options('fablib'):
        fablib = os.path.join(conf.FABLIB_MODULE_DIR, fablib_name)
        git_repo = conf.CONFIG.get('fablib', fablib_name)

        if not os.path.exists(fablib) and not api.env.is_test:
            cmd_gitclone = 'git clone {0} {1}'.format(git_repo, fablib)
            if util.confirm('{0} is not exists in fablib.\nDo you want to run "{1}"?'.format(fablib_name, cmd_gitclone), 'Canceled.'):  # noqa
                (status, output) = commands.getstatusoutput(cmd_gitclone)
                print output
                if status != 0:
                    exit(0)
            else:
                exit(0)


def create_required_dirs():
    create_dir(conf.STORAGE_DIR)
    create_dir(conf.DATABAG_DIR)
    create_dir(conf.LOG_DIR)
    create_dir(conf.TMP_DIR)
    create_dir(conf.NODE_DIR)
    create_dir(conf.FABSCRIPT_MODULE_DIR, True)
    create_dir(conf.FABLIB_MODULE_DIR, True)


def init_logger():
    # ALL_LOG_FILE_NAME = 'all.log'
    # ALL_LOG_FILE = os.path.join(conf.LOG_DIR, ALL_LOG_FILE_NAME)
    # ERROR_LOG_FILE_NAME = 'error.log'
    # ERROR_LOG_FILE = os.path.join(conf.LOG_DIR, ERROR_LOG_FILE_NAME)
    LOGGER_LEVEL = conf.CONFIG.get('logger', 'level')
    LOGGER_FORMAT = conf.CONFIG.get('logger', 'format', True)
    LOGGER_FORMATTER = logging.Formatter(fmt=LOGGER_FORMAT)
    LOGGER_CONSOLE_LEVEL = conf.CONFIG.get('logger', 'console_level')
    LOGGER_CONSOLE_LEVEL = getattr(logging, LOGGER_CONSOLE_LEVEL.upper())
    LOGGER_CONSOLE_FORMAT = conf.CONFIG.get('logger', 'console_format', True)
    LOGGER_CONSOLE_FORMATTER = logging.Formatter(fmt=LOGGER_CONSOLE_FORMAT)
    LOGGER_MAX_BYTES = conf.CONFIG.getint('logger', 'max_bytes')
    LOGGER_BACKUP_COUNT = conf.CONFIG.getint('logger', 'backup_count')
    NODE_LOGGER_MAX_BYTES = conf.CONFIG.getint('node_logger', 'max_bytes')
    NODE_LOGGER_BACKUP_COUNT = conf.CONFIG.getint('node_logger', 'backup_count')

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, conf.LOGGER_LEVEL.upper()))

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(conf.LOGGER_CONSOLE_FORMATTER)
    stream_handler.setLevel(conf.LOGGER_CONSOLE_LEVEL)
    root_logger.addHandler(stream_handler)

    file_rotaiting_handler = RotatingFileHandler(
        conf.ALL_LOG_FILE, 'a', conf.LOGGER_MAX_BYTES, conf.LOGGER_BACKUP_COUNT)
    file_rotaiting_handler.setFormatter(conf.LOGGER_FORMATTER)
    root_logger.addHandler(file_rotaiting_handler)

    error_file_rotaiting_handler = RotatingFileHandler(
        conf.ERROR_LOG_FILE, 'a', conf.LOGGER_MAX_BYTES, conf.LOGGER_BACKUP_COUNT)
    error_file_rotaiting_handler.setFormatter(conf.LOGGER_FORMATTER)
    error_file_rotaiting_handler.setLevel(logging.ERROR)
    root_logger.addHandler(error_file_rotaiting_handler)
