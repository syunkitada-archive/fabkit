# cording: utf-8

import os
import sys
import subprocess
import logging
from logging import StreamHandler
from logging.handlers import RotatingFileHandler
from fabkit import conf


def init_logger(cluster_name):
    root_logger = logging.getLogger()
    root_logger.setLevel(conf.LOGGER_LEVEL)

    # stream_handler = StreamHandler()
    # stream_handler.setFormatter(conf.LOGGER_CONSOLE_FORMATTER)
    # stream_handler.setLevel(conf.LOGGER_CONSOLE_LEVEL)
    # root_logger.addHandler(stream_handler)

    cluster_log_dir = os.path.join(conf.LOG_DIR, cluster_name)
    if not os.path.exists(cluster_log_dir):
        os.makedirs(cluster_log_dir)

    all_log_file = os.path.join(cluster_log_dir, conf.ALL_LOG_FILE_NAME)
    error_log_file = os.path.join(cluster_log_dir, conf.ERROR_LOG_FILE_NAME)
    stdout_log_file = os.path.join(cluster_log_dir, conf.STDOUT_LOG_FILE_NAME)

    file_rotaiting_handler = RotatingFileHandler(
        all_log_file, 'a', conf.LOGGER_MAX_BYTES, conf.LOGGER_BACKUP_COUNT)
    file_rotaiting_handler.setFormatter(conf.LOGGER_FORMATTER)
    root_logger.addHandler(file_rotaiting_handler)

    error_file_rotaiting_handler = RotatingFileHandler(
        error_log_file, 'a', conf.LOGGER_MAX_BYTES, conf.LOGGER_BACKUP_COUNT)
    error_file_rotaiting_handler.setFormatter(conf.LOGGER_FORMATTER)
    error_file_rotaiting_handler.setLevel(logging.ERROR)
    root_logger.addHandler(error_file_rotaiting_handler)

    # tee
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    tee = subprocess.Popen(["tee", stdout_log_file], stdin=subprocess.PIPE)
    os.dup2(tee.stdin.fileno(), sys.stdout.fileno())
    os.dup2(tee.stdin.fileno(), sys.stderr.fileno())
