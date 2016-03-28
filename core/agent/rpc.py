# coding: utf-8

import oslo_messaging as messaging
from oslo_config import cfg
from oslo_serialization import jsonutils
import fabcontext

CONF = cfg.CONF

_NAMESPACE = 'fabkit'
_TOPIC = 'fabkit'


class BaseRPCAPI(object):
    """Server side of the base RPC API."""

    def __init__(self, service_name, target):
        self.target = target
        self.service_name = service_name

    def ping(self, context, arg):
        resp = {'service': self.service_name, 'arg': arg}
        return jsonutils.to_primitive(resp)


class BaseAPI(object):
    def __init__(self, target):
        self.target = target
        transport = messaging.get_transport(CONF)
        self.client = messaging.RPCClient(transport, target)


def get_server(target, endpoints, serializer=None):
    transport = messaging.get_transport(CONF)
    serializer = RequestContextSerializer(serializer)

    # https://bugs.launchpad.net/searchlight/+bug/1548260
    # Start a non-daemon listener service with at least 1 worker,
    # when press ctrl + c to terminate the service, some oslo messaging error messages show,
    # and the worker process doesn't exit, it's still running.
    # self.rpc_server = messaging.get_rpc_server(
    #     transport, target, self.rpc_endpoints, executor='eventlet')

    return messaging.get_rpc_server(transport,
                                    target,
                                    endpoints,
                                    executor='threading',
                                    serializer=serializer)


class RequestContextSerializer(messaging.Serializer):

    def __init__(self, base):
        self._base = base

    def serialize_entity(self, context, entity):
        if not self._base:
            return entity
        return self._base.serialize_entity(context, entity)

    def deserialize_entity(self, context, entity):
        if not self._base:
            return entity
        return self._base.deserialize_entity(context, entity)

    def serialize_context(self, context):
        return context.to_dict()

    def deserialize_context(self, context):
        return fabcontext.RequestContext.from_dict(context)
