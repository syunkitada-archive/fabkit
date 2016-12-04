# coding: utf-8

import datetime
from oslo_config import cfg
from oslo_db.sqlalchemy import session as db_session
from sqlalchemy.orm import exc
from sqlalchemy import desc
from impl_sqlalchemy import models
from fabkit import util
from oslo_log import log as logging

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


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

    def get_active_cental_agents(self):
        query = self.session.query(models.Agent)
        agents = query.filter(
            models.Agent.agent_type == 'central',
            models.Agent.status == 'active').order_by(desc(models.Agent.id)).all()
        return agents

    def get_agents(self):
        query = self.session.query(models.Agent)
        agents = query.filter().all()
        return agents

    def get_events(self):
        query = self.session.query(models.Event)
        events = query.filter().all()
        return events

    def check_agents(self):
        agents = self.get_agents()

        events = []
        now = datetime.datetime.utcnow()
        with self.session.begin():
            for agent in agents:
                if CONF.agent.agent_downtime > (now - agent.check_timestamp).total_seconds():
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

    def create_task(self, task_data):
        task = models.Task(**task_data)
        with self.session.begin():
            self.session.add(task)

    def get_last_job(self, method, target):
        query = self.session.query(models.Task)
        task = query.filter(models.Task.method == method,
                            models.Task.target == target).order_by(
                                models.Task.updated_at.desc()).first()
        return task

    def get_tasks(self, method=None, active=True, status=None):
        query = self.session.query(models.Task)
        if status is None:
            if method is None:
                tasks = query.filter(models.Task.active == active).all()
            else:
                tasks = query.filter(models.Task.method == method,
                                     models.Task.active == active).all()
        else:
            if method is None:
                tasks = query.filter(models.Task.active == active,
                                     models.Task.status == status).all()
            else:
                tasks = query.filter(models.Task.method == method,
                                     models.Task.status == status,
                                     models.Task.active == active).all()
        return tasks

    def get_all_tasks(self, limit=100):
        query = self.session.query(models.Task)
        tasks = query.order_by(desc(models.Task.created_at)).limit(limit).all()
        return tasks

    def cancel_my_tasks(self):
        query = self.session.query(models.Task)
        tasks = query.filter(models.Task.active,
                             models.Task.owner == CONF.host).all()

        with self.session.begin():
            for task in tasks:
                task.status = 'canceled'
                task.active = False
                LOG.info("Canceled {0}'s task: {1} {2}".format(
                    task.owner, task.method, task.target))

    def get_request_tasks(self, method=None):
        query = self.session.query(models.Task)
        if method is None:
            tasks = query.filter(models.Task.active,
                                 models.Task.status == 'requested').all()

        else:
            tasks = query.filter(models.Task.active,
                                 models.Task.status == 'requested',
                                 models.Task.method == method).all()

        return tasks

    def update_task_status(self, current_status=None, status=None, active=None, msg=None,
                           task=None, method=None, target=None, owner=None):
        query = self.session.query(models.Task)
        with self.session.begin():
            if task is None:
                tasks = query.filter(models.Task.method == method,
                                     models.Task.target == target,
                                     models.Task.status == current_status).all()
                if len(tasks) == 1:
                    task = tasks[0]

            if task is not None:
                task.status = status
                if owner is not None:
                    task.owner = owner
                if active is not None:
                    task.active = active
                if msg is not None:
                    task.msg = msg

                LOG.info('Updated task: {0} {1}'.format(method, target))
            else:
                LOG.warn('Task not found: {0} {1}'.format(method, target))

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
            seconds=CONF.agent.delete_event_interval)

        with self.session.begin():
            query.filter(models.Event.hooked == 1,
                         models.Event.created_at < delete_event_at).delete()
