# coding: utf-8

from base import genconfig, sync_fablib, sync_db  # noqa
from client import client

genconfig.__doc__ = """
Generate config.
"""

sync_fablib.__doc__ = """
Sync fablib.
"""

client.__doc__ = """
Download fabric-repo from swift, and run $ fab setup:local.
"""

sync_db.__doc__ = """
Sync db.
"""
