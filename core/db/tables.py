# coding: utf-8

from sqlalchemy import (Table, MetaData, Column, String, Text, Integer,
                        SmallInteger, CHAR, DateTime, Enum, Boolean, Unicode,
                        UniqueConstraint, ForeignKeyConstraint)

from oslo_config import cfg
from oslo_utils import timeutils


quotas = Table('quotas', metadata,
    Column('id', UUID, default=utils.generate_uuid, primary_key=True),
    Column('version', Integer, default=1, nullable=False),
    Column('created_at', DateTime, default=lambda: timeutils.utcnow()),
    Column('updated_at', DateTime, onupdate=lambda: timeutils.utcnow()),

    Column('tenant_id', String(36), default=None, nullable=True),
    Column('resource', String(32), nullable=False),
    Column('hard_limit', Integer, nullable=False),

    mysql_engine='InnoDB',
    mysql_charset='utf8',
)

