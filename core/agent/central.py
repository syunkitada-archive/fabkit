# coding: utf-8

from db import dbapi
import datetime
import service
import rpc
import agent
from oslo_service import periodic_task
from oslo_config import cfg
from oslo_log import log as logging
from oslo_serialization import jsonutils
import oslo_messaging as messaging

CONF = cfg.CONF
central_dbapi = dbapi.DBAPI()
LOG = logging.getLogger(__name__)


class CentralManager(periodic_task.PeriodicTasks):
    def __init__(self):
        super(CentralManager, self).__init__(CONF)
        self.service_name = 'agent'
        self.central_dbapi = dbapi.DBAPI()

    def periodic_tasks(self, context, raise_on_error=False):
        return self.run_periodic_tasks(context, raise_on_error=raise_on_error)

    @periodic_task.periodic_task(spacing=3)
    def hello(self, context):
        LOG.info('hello')
        print 'hello'

    @periodic_task.periodic_task(spacing=CONF._check_agent_interval)
    def check_agent(self, context):
        LOG.info('check_agent')
        self.central_dbapi.check_agents()

    @periodic_task.periodic_task(spacing=CONF.client.check_event_interval)
    def check_event(self, context):
        LOG.info('check_event')
        self.central_dbapi.check_events()

    @periodic_task.periodic_task(spacing=CONF.client.delete_event_interval)
    def delete_event(self, context):
        LOG.info('delete_event')
        self.central_dbapi.delete_events()


class CentralRPCAPI(rpc.BaseRPCAPI):
    def __init__(self):
        target = messaging.Target(topic='central', version='2.0', server='server1')
        self.central_dbapi = dbapi.DBAPI()
        super(CentralRPCAPI, self).__init__('central', target)

    def setup(self, context, arg):
        LOG.info('setup')
        agentapi = agent.AgentAPI()
        result = agentapi.setup()
        print result
        resp = {'result': result}
        return jsonutils.to_primitive(resp)

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

    def notify(self, context, agent_data):
        LOG.info('notify')
        self.central_dbapi.create_or_update_agent(agent_data)

    def disable_node(self, context, arg):
        print 'disable node'

    def enable_node(self, context, arg):
        print 'disable node'


class CentralAPI(rpc.BaseAPI):
    def __init__(self):
        target = messaging.Target(topic='central', version='2.0')
        super(CentralAPI, self).__init__(target)

    def setup(self):
        return self.client.call({}, 'setup', arg='')

    def notify(self, agent_data):
        return self.client.call({}, 'notify', agent_data=agent_data)


class CentralService(service.Service):

    def __init__(self):
        super(CentralService, self).__init__(CentralManager(), CentralRPCAPI())
