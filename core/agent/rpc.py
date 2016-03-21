# coding: utf-8

import oslo_messaging as messaging
from oslo_config import cfg
from oslo_serialization import jsonutils
import fabcontext

CONF = cfg.CONF

_NAMESPACE = 'fabkit'


class BaseRPCAPI(object):
    """Server side of the base RPC API."""

    target = messaging.Target(namespace=_NAMESPACE, version='1.1')

    def __init__(self, service_name, backdoor_port):
        self.service_name = service_name
        self.backdoor_port = backdoor_port

    def ping(self, context, arg):
        resp = {'service': self.service_name, 'arg': arg}
        return jsonutils.to_primitive(resp)

    def get_backdoor_port(self, context):
        return self.backdoor_port


def get_server(target, endpoints, serializer=None):
    transport = messaging.get_transport(CONF)
    serializer = RequestContextSerializer(serializer)
    return messaging.get_rpc_server(transport,
                                    target,
                                    endpoints,
                                    executor='eventlet',
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
