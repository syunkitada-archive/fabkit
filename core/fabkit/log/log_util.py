# cording: utf-8

import os
import logging
from logging.handlers import RotatingFileHandler
from oslo_config import cfg
from fabkit import env

CONF = cfg.CONF


def init_logger(cluster_name):
    root_logger = logging.getLogger()
    root_logger.setLevel(CONF.logger.level.upper())

    cluster_log_dir = os.path.join(CONF._log_dir, cluster_name)
    if not os.path.exists(cluster_log_dir):
        os.makedirs(cluster_log_dir)

    all_log_file = os.path.join(cluster_log_dir, CONF._all_log_file_name)
    error_log_file = os.path.join(cluster_log_dir, CONF._error_log_file_name)

    file_rotaiting_handler = RotatingFileHandler(
        all_log_file, 'a', CONF.logger.max_bytes, CONF.logger.backup_count)
    file_rotaiting_handler.setFormatter(CONF._logger_formatter)
    root_logger.addHandler(file_rotaiting_handler)

    error_file_rotaiting_handler = RotatingFileHandler(
        error_log_file, 'a', CONF.logger.max_bytes, CONF.logger.backup_count)
    error_file_rotaiting_handler.setFormatter(CONF._logger_formatter)
    error_file_rotaiting_handler.setLevel(logging.ERROR)
    root_logger.addHandler(error_file_rotaiting_handler)

    env.console_file = os.path.join(CONF._node_dir, cluster_name, "__console.log")
    with open(env.console_file, "w") as f:
        f.write("Init {0} console.log\n".format(cluster_name))
