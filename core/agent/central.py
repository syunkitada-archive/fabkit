# coding: utf-8

from db import dbapi
from service import Service
from rpc import BaseRPCAPI, BaseAPI
from oslo_service import periodic_task
from oslo_config import cfg
from oslo_log import log as logging
from oslo_serialization import jsonutils
import oslo_messaging as messaging
from agent import AgentAPI

CONF = cfg.CONF
central_dbapi = dbapi.DBAPI()
LOG = logging.getLogger(__name__)


class CentralManager(periodic_task.PeriodicTasks):
    def __init__(self):
        super(CentralManager, self).__init__(CONF)
        self.service_name = 'agent'

    def periodic_tasks(self, context, raise_on_error=False):
        return self.run_periodic_tasks(context, raise_on_error=raise_on_error)

    @periodic_task.periodic_task(spacing=3)
    def hello(self, context):
        LOG.info('hello')
        print 'hello'

    @periodic_task.periodic_task(spacing=CONF._check_agent_interval)
    def check_agent(self, context):
        LOG.info('check_agent')


class CentralRPCAPI(BaseRPCAPI):
    def __init__(self):
        target = messaging.Target(topic='central', version='2.0', server='server1')
        super(CentralRPCAPI, self).__init__('central', target)

    def setup(self, context, arg):
        LOG.info('setup')
        agentapi = AgentAPI()
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

    def update_agent(self, context, arg):
        """
        store metrics
        store server status
        """
        print 'store'
        context['host']
        context['agent_type']
        context['heartbeat_timestamp']
        central_dbapi.update_agent()

    def disable_node(self, context, arg):
        print 'disable node'

    def enable_node(self, context, arg):
        print 'disable node'


class CentralAPI(BaseAPI):
    def __init__(self):
        target = messaging.Target(topic='central', version='2.0')
        super(CentralAPI, self).__init__(target)

    def setup(self):
        return self.client.call({}, 'setup', arg='')


class CentralService(Service):

    def __init__(self):
        super(CentralService, self).__init__(CentralManager(), CentralRPCAPI())
