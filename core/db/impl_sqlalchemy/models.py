# coding: utf-8

import datetime
from oslo_db.sqlalchemy import models
from sqlalchemy import (Column, Integer, String, ForeignKey, Index, DateTime,
                        Boolean, UniqueConstraint, BigInteger, MetaData)

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

    # active, down, disable
    status = Column(String(55), nullable=False)

    # check
    check_status = Column(Integer, nullable=False)
    check_timestamp = Column(DateTime, nullable=False)

    # setup
    setup_status = Column(String(55), nullable=False)
    setup_timestamp = Column(DateTime, nullable=False)

    # fabscript_map
    fabscript_map = Column(String(1000), nullable=False)


class Event(Base):
    __tablename__ = 'event'
    # check, setup
    event_type = Column(String(255), nullable=False)
    host = Column(String(255), nullable=False)
    fabscript = Column(String(255), nullable=False)
    msg = Column(String(255), nullable=False)
    status = Column(Integer(), nullable=False)
    hooked = Column(Boolean(), nullable=False, default=False)
