# coding: utf-8

from fabric import api
import commands, re, os
import conf, util
import logging
from logging.handlers import RotatingFileHandler

loggers = {}
def get_logger(host=None):
    if not host:
        host = api.env.host

    if host is None:
        return logging

    logger = None
    if host in loggers:
        logger = loggers[host]
    else:
        logger = logging.getLogger(host)
        logger.setLevel(conf.LOGGER_LEVEL)
        handler = RotatingFileHandler(get_node_log(host), 'a', conf.NODE_LOGGER_MAX_BYTES, conf.NODE_LOGGER_BACKUP_COUNT)
        handler.setFormatter(conf.LOGGER_FORMATTER)
        logger.addHandler(handler)
        loggers.update({host: logger})

    return logger

def get_node_logdir(host=None):
    node_logdir = os.path.join(conf.LOG_DIR, host)
    if not os.path.exists(node_logdir):
        os.mkdir(node_logdir)
    return node_logdir

def get_node_log(host=None):
    return os.path.join(get_node_logdir(host), '{0}.log'.format(host))

def get_node_log_json_file(host=None):
    return os.path.join(get_node_logdir(host), 'status.json')

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

