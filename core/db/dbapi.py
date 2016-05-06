# coding: utf-8

import datetime
from oslo_config import cfg
from oslo_db.sqlalchemy import session as db_session
from sqlalchemy.orm import exc
from impl_sqlalchemy import models
from fabkit import util

CONF = cfg.CONF


class DBAPI():

    def __init__(self, url=None):
        options = dict(CONF.database.items())
        if url is None:
            url = options['connection']
        self.engine_facade = db_session.EngineFacade(url, **options)
        self.session = self.engine_facade.get_session()

    def create_or_update_agent(self, agent_data):
        with self.session.begin():
            try:
                agent = self.get_agent(agent_data['agent_type'], agent_data['host'])
                agent.update(agent_data)

            except exc.NoResultFound:
                agent_data['check_timestamp'] = datetime.datetime.utcnow()
                agent = models.Agent(**agent_data)
                self.session.add(agent)

        return agent

    def get_session(self):
        return self.session

    def get_agent(self, agent_type, host):
        query = self.session.query(models.Agent)
        agent = query.filter(models.Agent.agent_type == agent_type,
                             models.Agent.host == host).one()
        return agent

    def get_agents(self):
        query = self.session.query(models.Agent)
        agents = query.filter().all()
        return agents

    def check_agents(self):
        agents = self.get_agents()

        events = []
        now = datetime.datetime.utcnow()
        with self.session.begin():
            for agent in agents:
                if CONF.client.agent_downtime > (now - agent.check_timestamp).total_seconds():
                    if agent.status == 'down':
                        self.create_event({
                            'host': agent.host,
                            'event_type': 'check',
                            'fabscript': 'check_timestamp',
                            'msg': 'status change from down to active',
                            'status': 0,
                        })

                    agent.status = 'active'
                else:
                    if agent.status == 'active':
                        self.create_event({
                            'host': agent.host,
                            'event_type': 'check',
                            'fabscript': 'check_timestamp',
                            'msg': 'status change from active to down',
                            'status': 10000,
                        })

                    agent.status = 'down'

        for event in events:
            self.create_event(self, event)

    def create_event(self, event_data):
        event = models.Event(**event_data)
        self.session.add(event)

    def check_events(self):
        query = self.session.query(models.Event)
        events = query.filter(models.Event.hooked == 0).all()

        util.event_handler.hook(events)
        with self.session.begin():
            for event in events:
                event.hooked = 1

    def delete_events(self):
        query = self.session.query(models.Event)
        current_time = datetime.datetime.utcnow()
        delete_event_at = current_time - datetime.timedelta(
            seconds=CONF.client.delete_event_interval)

        with self.session.begin():
            query.filter(models.Event.hooked == 1,
                         models.Event.created_at < delete_event_at).delete()
