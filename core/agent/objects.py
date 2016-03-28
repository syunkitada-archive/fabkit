# coding: utf-8

from oslo_versionedobjects import base as ovoo_base
import oslo_messaging as messaging


class FabObject(ovoo_base.VersionedObject):
    pass


class FabObjectSerializer(messaging.NoOpSerializer):
    pass
