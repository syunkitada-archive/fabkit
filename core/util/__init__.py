# coding: utf-8

from base import genconfig, sync_fablib, sync_db, create_dns_domain, create_dns_record  # noqa
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

create_dns_domain.__doc__ = """
Create domain.

fab create_dns_domain:example.com
"""


create_dns_record.__doc__ = """
Create record.

fab create_dns_record:hoge,example.com,A,127.0.0.1
"""
