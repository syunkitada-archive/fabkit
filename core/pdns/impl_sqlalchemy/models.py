# coding: utf-8

import datetime
from oslo_db.sqlalchemy import models
from sqlalchemy import (Column, Integer, String, Text, ForeignKey, Index, DateTime, SmallInteger,
                        Boolean, UniqueConstraint, BigInteger, MetaData)

from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData()


class BaseCommon(models.ModelBase):
    """Base class for Neutron Models."""

    id = Column(Integer, primary_key=True, autoincrement=True)
    __table_args__ = {'mysql_engine': 'InnoDB'}


Base = declarative_base(cls=BaseCommon)


class Domains(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    __tablename__ = 'domains'
    __table_args__ = (
        Index('domains_name', 'name'),
        {'mysql_engine': 'InnoDB'},
    )
    name = Column(String(255), nullable=False)
    master = Column(String(255), default=None)
    last_check = Column(Integer(), default=None)
    type = Column(String(6), nullable=False)
    notified_serial = Column(Integer(), default=None)
    account = Column(String(40), default=None)


class Records(Base):
    __tablename__ = 'records'
    __table_args__ = (
        Index('records_domain_id', 'domain_id'),
        Index('records_name_type', 'name', 'type'),
        Index('records_domain_id_ordername', 'domain_id', 'ordername'),
        {'mysql_engine': 'InnoDB'},
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    domain_id = Column(Integer(), default=None)
    name = Column(String(255), default=None)
    type = Column(String(6), default=None)
    content = Column(String(255), default=None)
    ttl = Column(Integer(), default=None)
    prio = Column(Integer(), default=None)
    change_date = Column(Integer(), default=None)
    disabled = Column(SmallInteger(), default=0, nullable=False)
    ordername = Column(String(255), default=None)
    auth = Column(SmallInteger(), default=1, nullable=False)


class Supermasters(Base):
    __table_args__ = (
        {'mysql_engine': 'InnoDB'},
    )
    __tablename__ = 'supermasters'
    ip = Column(String(64), nullable=False, primary_key=True)
    nameserver = Column(String(255), nullable=False, primary_key=True)
    account = Column(String(40), nullable=False)


class Comments(Base):
    __tablename__ = 'comments'
    __table_args__ = (
        Index('comments_domain_id', 'domain_id'),
        Index('comments_name_type', 'name', 'type'),
        Index('comments_domain_id_modified_at', 'domain_id', 'modified_at'),
        {'mysql_engine': 'InnoDB'},
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    domain_id = Column(Integer(), index=True, nullable=False)
    name = Column(String(255), index=True, nullable=False)
    type = Column(String(10), index=True, nullable=False)
    modified_at = Column(Integer(), index=True, nullable=False)
    account = Column(String(40), nullable=False)
    comment = Column(String(64000), nullable=False)


class Domainmetadata(Base):
    __tablename__ = 'domainmetadata'
    __table_args__ = (
        Index('domainmetadata_domain_id_kind', 'domain_id', 'kind'),
        {'mysql_engine': 'InnoDB'},
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    domain_id = Column(Integer(), nullable=False)
    kind = Column(String(32), nullable=False)
    content = Column(Text(), nullable=False)


class Cryptokeys(Base):
    __tablename__ = 'cryptokeys'
    __table_args__ = (
        Index('cryptokeys_domain_id', 'domain_id'),
        {'mysql_engine': 'InnoDB'},
    )
    domain_id = Column(Integer(), nullable=False)
    flags = Column(Integer(), nullable=False)
    active = Column(Boolean(), default=None)
    content = Column(Text(), default=None)


class Tsigkeys(Base):
    __tablename__ = 'tsigkeys'
    __table_args__ = (
        Index('tsigkeys_name_algorithm', 'name', 'algorithm'),
        {'mysql_engine': 'InnoDB'},
    )
    name = Column(String(50), default=None)
    algorithm = Column(String(50), default=None)
    secret = Column(String(255), default=None)
