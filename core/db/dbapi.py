# coding: utf-8

import datetime
from oslo_config import cfg
from oslo_db.sqlalchemy import session as db_session
from sqlalchemy.orm import exc
from impl_sqlalchemy.models import Agent

CONF = cfg.CONF


class DBAPI():

    def __init__(self, target='central'):
        options = dict(CONF.database.items())
        url = options['connection']
        self.engine_facade = db_session.EngineFacade(url, **options)
        self.session = self.engine_facade.get_session()

    def create_or_update_agent(self, agent_data):
        with self.session.begin():
            try:
                agent = self.get_agent(agent_data['agent_type'], agent_data['host'])
                agent_data['heartbeat_timestamp'] = datetime.datetime.utcnow()
                agent.update(agent_data)

            except exc.NoResultFound:
                print 'DEBUG'
                agent_data['heartbeat_timestamp'] = datetime.datetime.utcnow()
                agent = Agent(**agent_data)
                self.session.add(agent)

        return agent

    def get_agent(self, agent_type, host):
        query = self.session.query(Agent)
        agent = query.filter(Agent.agent_type == agent_type,
                             Agent.host == host).one()
        return agent
