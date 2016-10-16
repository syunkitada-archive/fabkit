# coding: utf-8

import yaml
import eventlet
import json
import datetime
from db import dbapi
import service
import rpc
import agent
from oslo_service import periodic_task
from oslo_config import cfg
from oslo_log import log as logging
from oslo_serialization import jsonutils
import oslo_messaging as messaging
from util import client

CONF = cfg.CONF
LOG = logging.getLogger(__name__)
eventlet.monkey_patch()


class CentralManager(periodic_task.PeriodicTasks):
    def __init__(self):
        super(CentralManager, self).__init__(CONF)
        self.service_name = 'agent'
        self.central_dbapi = dbapi.DBAPI()
        self.centralapi = CentralAPI()
        self.agentapi = agent.AgentAPI()
        self.load_jobs()

    def load_jobs(self):
        LOG.info('Load jobs')
        with open(CONF._job_yml) as f:
            job_data = yaml.load(f)
        self.job_map = job_data['job_map']

    def periodic_tasks(self, context, raise_on_error=False):
        return self.run_periodic_tasks(context, raise_on_error=raise_on_error)

    def is_master(self):
        central_agents = self.central_dbapi.get_active_cental_agents()
        if len(central_agents) > 0 and central_agents[0].host == CONF.host:
            return True
        return False

    @periodic_task.periodic_task(spacing=CONF._check_agent_interval)
    def check_agent(self, context):
        LOG.info('check_agent')
        self.central_dbapi.check_agents()

    @periodic_task.periodic_task(spacing=CONF.agent.check_event_interval)
    def check_event(self, context):
        if self.is_master():
            LOG.info('check_event')
            self.central_dbapi.check_events()
        else:
            LOG.info('check_event: skipped')

    # @periodic_task.periodic_task(spacing=CONF.agent.check_task_interval)
    @periodic_task.periodic_task(spacing=10)
    def check_task(self, context):
        if self.is_master():
            LOG.info('check_task')
            requested_tasks = self.central_dbapi.get_tasks(status='requested')
            requested_task_map = {}
            for task in requested_tasks:
                requested_task_map[task.method + task.target] = task

            queued_tasks = self.central_dbapi.get_tasks(status='queued')
            queued_task_map = {}
            for task in queued_tasks:
                queued_task_map[task.method + task.target] = task

            for task in requested_tasks:
                LOG.info('Requested task: {0}-{1}({2})'.format(
                    task.method, task.target, task.json_arg))
                arg = json.loads(task.json_arg)
                if task.method == 'setup':
                    self.central_dbapi.update_task_status(task=task, status='queued')
                    if task.pallalel > -1:
                        arg['random_wait'] = task.pallalel
                        self.agentapi.setup(arg=arg)
                    else:
                        # TODO serial setup
                        LOG.warn('serial setup, but not implement')

                elif task.method == 'job':
                    self.central_dbapi.update_task_status(task=task, status='queued')
                    self.centralapi.job(arg=arg)

            current_time = datetime.datetime.utcnow()
            LOG.info('create_jobs')
            for category, jobs in self.job_map.items():
                for job in jobs:
                    enable_job = False
                    job_name = job['name']
                    key = 'job' + job_name
                    if key not in queued_task_map and key not in requested_task_map:
                        last_job = self.central_dbapi.get_last_job('job', job_name)
                        if last_job is not None:
                            LOG.info('Last job {0} at {1}'.format(key, last_job.updated_at))
                            job_span = job.get('span')
                            if job_span is not None:
                                time = int(job_span[0:-1])
                                time_type = job_span[-1]
                                if time_type == 's':
                                    time_span = datetime.timedelta(seconds=time)

                                next_job_time = last_job.updated_at + time_span
                                if current_time > next_job_time:
                                    enable_job = True
                                else:
                                    LOG.info('Skip job {0} at {1}, wait span'.format(
                                        key, last_job.updated_at))
                        else:
                            enable_job = True

                        if enable_job:
                            self.central_dbapi.create_task({
                                'method': 'job',
                                'json_arg': json.dumps(job),
                                'target': job_name,
                                'pallalel': -1,
                            })
                            LOG.info('Created job {0}'.format(job_name))

        else:
            LOG.info('check_task: skipped')

    @periodic_task.periodic_task(spacing=CONF.agent.delete_event_interval)
    def delete_event(self, context):
        LOG.info('delete_event')
        self.central_dbapi.delete_events()

    @periodic_task.periodic_task(spacing=CONF.agent.agent_report_interval)
    def check(self, context):
        LOG.info('start check')

        agent_data = {
            'agent_type': 'central',
            'host': CONF.host,
            'status': 'active',
            'setup_status': 0,
            'setup_timestamp': datetime.datetime.utcnow(),
            'check_status': 0,
            'check_timestamp': datetime.datetime.utcnow(),
            'fabscript_map': '{}',
        }

        self.centralapi.notify_check(agent_data)


class CentralRPCAPI(rpc.BaseRPCAPI):
    def __init__(self):
        target = messaging.Target(topic='central', version='2.0', server='server1')
        self.central_dbapi = dbapi.DBAPI()
        super(CentralRPCAPI, self).__init__('central', target)

    def hello(self, context, arg):
        LOG.info('rpc hello')
        return 'hello called'

    def setup(self, context, arg):
        LOG.info('setup')
        agentapi = agent.AgentAPI()
        result = agentapi.setup()
        resp = {'result': result}
        return jsonutils.to_primitive(resp)

    def start_job(self, context, job):
        LOG.info('start job')
        cluster = job['cluster']
        result_map = client('job', cluster)
        print '\n\n\nDEBUG start job'
        print result_map

        central_dbapi = dbapi.DBAPI()
        central_dbapi.update_task_status(current_status='queued',
                                         status='completed', method='job', target=job['name'])
        LOG.info('end job')
        return

    def job(self, context, arg):
        LOG.info('rpc job')
        eventlet.spawn(self.start_job, context, arg)
        return 'job called'

    def manage(self, context, arg):
        """
        store metrics
        store server status
        """
        print 'store'

    def alarm(self, context, arg):
        """
        alarm message
        store server status
        """
        print 'alarm'

    def notify_check(self, context, agent_data):
        LOG.info('notify')
        self.central_dbapi.create_or_update_agent(agent_data)

    def notify_setup(self, context, agent_data):
        LOG.info('notify_setup')
        self.central_dbapi.create_or_update_agent(agent_data)

    def disable_node(self, context, arg):
        print 'disable node'

    def enable_node(self, context, arg):
        print 'disable node'


class CentralAPI(rpc.BaseAPI):
    def __init__(self):
        target = messaging.Target(topic='central', version='2.0')
        super(CentralAPI, self).__init__(target)

    def hello(self):
        return self.client.call({}, 'hello', arg='')

    def setup(self):
        return self.client.call({}, 'setup', arg='')

    def job(self, arg):
        return self.client.cast({}, 'job', arg=arg)

    def notify_check(self, agent_data):
        return self.client.call({}, 'notify_check', agent_data=agent_data)

    def notify_setup(self, agent_data):
        return self.client.call({}, 'notify_setup', agent_data=agent_data)


class CentralService(service.Service):

    def __init__(self):
        super(CentralService, self).__init__(CentralManager(), CentralRPCAPI())
