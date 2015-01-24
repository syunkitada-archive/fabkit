# cording: utf-8

import os
import sys
import subprocess
import logging
from logging import StreamHandler
from logging.handlers import RotatingFileHandler
from fabkit import conf, env


def init_logger():
    print 'test'
    root_logger = logging.getLogger()
    root_logger.setLevel(conf.LOGGER_LEVEL)

    stream_handler = StreamHandler()
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


def set_stdout_pipe():
    len_env_tasks = len(env.tasks)
    if len_env_tasks > 0:
        if len_env_tasks > 1 and env.tasks[0].find('node') == 0:
            # | tee STDOUT_LOG_FILE
            # Unbuffer output
            sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

            tee = subprocess.Popen(["tee", conf.STDOUT_LOG_FILE], stdin=subprocess.PIPE)
            os.dup2(tee.stdin.fileno(), sys.stdout.fileno())
            os.dup2(tee.stdin.fileno(), sys.stderr.fileno())
