# coding: utf-8

import rpc
import objects
from oslo_service import service
from oslo_config import cfg
from oslo_log import log as logging

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class Service(service.Service):

    def __init__(self, manager, rpc_api):
        super(Service, self).__init__()
        LOG.info('init service')

        # policy.init()
        # rpc.init()
        # self.host

        self.manager = manager
        self.timers = []

        self.rpc_endpoints = [rpc_api]
        serializer = objects.FabObjectSerializer()
        self.rpc_server = rpc.get_server(rpc_api.target, self.rpc_endpoints, serializer)

    def start(self, *args, **kwargs):
        super(Service, self).start()
        LOG.info('start service')

        self.rpc_server.start()

        self.tg.add_dynamic_timer(self.periodic_tasks,
                                  initial_delay=0,
                                  periodic_interval_max=120)

    def periodic_tasks(self, raise_on_error=False):
        ctxt = {}
        return self.manager.periodic_tasks(ctxt, raise_on_error=raise_on_error)

    def wait(self):
        LOG.info('wait service')

    def stop(self):
        LOG.info('stop service')
        super(Service, self).stop()

        try:
            self.rpcserver.stop()
            self.rpcserver.wait()
        except Exception:
            pass
