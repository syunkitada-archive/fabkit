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
