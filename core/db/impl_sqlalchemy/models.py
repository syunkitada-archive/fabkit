# coding: utf-8

import datetime
from oslo_db.sqlalchemy import models
from sqlalchemy import (Column, Integer, String, ForeignKey, Index, DateTime,
                        UniqueConstraint, BigInteger, MetaData)

from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData()


class FabkitBase(models.ModelBase):
    """Base class for Neutron Models."""

    id = Column(Integer, primary_key=True, autoincrement=True)
    __table_args__ = {'mysql_engine': 'InnoDB'}

    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow,
                        onupdate=datetime.datetime.utcnow)


Base = declarative_base(cls=FabkitBase)


class Agent(Base):
    __tablename__ = 'agent'
    # agent, central
    agent_type = Column(String(255), nullable=False)
    # TOPIC.host is a target topic
    host = Column(String(255), nullable=False)
    # updated when agents report
    heartbeat_timestamp = Column(DateTime, nullable=False)
    # active, down, disable
    status = Column(String(55), nullable=False)
    # ok, warning, critical
    err_status = Column(String(55), nullable=False)
    # warn errors
    warn_errs_len = Column(Integer, nullable=False)
    # count crit total_errors
    crit_errs_len = Column(Integer, nullable=False)
    # json warn errors: [{"title": "hoge", "status": "warn", "msg": "hoge"}, ...]
    warn_errs = Column(String(1000), nullable=False)
    # json crit errors: [{"title": "hoge", "status": "crit", "msg": "hoge"}, ...]
    crit_errs = Column(String(1000), nullable=False)


class Alarm(Base):
    __tablename__ = 'alarm'
    host = Column(String(255), nullable=False)
    title = Column(String(55), nullable=False)
    msg = Column(String(255), nullable=False)
    status = Column(String(55), nullable=False)
    task = Column(String(55), nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
