# coding: utf-8

import os
import logging
from logging.handlers import RotatingFileHandler
from fabkit import conf, env, api


loggers = {}


def get_logger(host=None):
    if host is None:
        host = api.env.host
    cluster_name = env.cluster.get('name')
    if host is None or cluster_name is None:
        return logging

    host = cluster_name + '/' + host

    logger = None
    if host in loggers:
        logger = loggers[host]
    else:
        logger = logging.getLogger(host)
        logger.setLevel(conf.LOGGER_LEVEL)
        log_file = os.path.join(conf.LOG_DIR, '{0}.log'.format(host))

        handler = RotatingFileHandler(log_file,
                                      'a', conf.NODE_LOGGER_MAX_BYTES,
                                      conf.NODE_LOGGER_BACKUP_COUNT)
        handler.setFormatter(conf.LOGGER_FORMATTER)
        logger.addHandler(handler)
        loggers.update({host: logger})

    return logger


def debug(msg, host=None):
    get_logger(host).debug(msg)


def info(msg, host=None):
    get_logger(host).info(msg)


def warning(msg, host=None):
    get_logger(host).warning(msg)


def error(msg, host=None):
    get_logger(host).error(msg)


def critical(msg, host=None):
    get_logger(host).critical(msg)
