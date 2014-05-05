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

    logger = None
    if host in loggers:
        logger = loggers[host]
    else:
        logger = logging.getLogger(host)
        logger.setLevel(conf.LOGGER_LEVEL)
        handler = RotatingFileHandler(os.path.join(conf.LOG_DIR, '{0}.log'.format(host)), 'a', conf.NODE_LOGGER_MAX_BYTES, conf.NODE_LOGGER_BACKUP_COUNT)
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

