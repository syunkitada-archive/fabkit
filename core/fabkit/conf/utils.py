# coding: utf-8


import os
from oslo_config import cfg


CONF = cfg.CONF


def complement_path(path):
    if path == '':
        return None
    if path.find('/') == 0:
        return path
    elif path.find('~') == 0:
        return os.path.expanduser(path)

    return os.path.join(CONF._repo_dir, path)
