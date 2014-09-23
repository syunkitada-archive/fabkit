# coding: utf-8

import ConfigParser


class Config():
    def __init__(file_path, file_format):
        config = ConfigParser.SafeConfigParser()
        config.read('/etc/keystone/keystone.config')
