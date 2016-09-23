# noqa

import os
from libvirt import Libvirt  # noqa
from docker import Docker  # noqa


def create(container):
    print 'DEBUG'
    print container
    if container['provider'] == 'libvirt':
        libvirt = Libvirt(container)
        libvirt.setup()
