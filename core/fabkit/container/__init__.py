# noqa

from libvirt import Libvirt  # noqa
from docker import Docker  # noqa


def create(container):
    if container['provider'] == 'libvirt':
        libvirt = Libvirt(container)
        libvirt.create()


def delete(container):
    if container['provider'] == 'libvirt':
        libvirt = Libvirt(container)
        libvirt.delete()
