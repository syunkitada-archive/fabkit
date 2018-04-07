# cording: utf-8

import random
import uuid
import time
from fabkit import filer, sudo, api, run
from oslo_config import cfg
from netaddr import IPNetwork
from pdns import pdnsapi
import os

CONF = cfg.CONF


class Libvirt():
    def __init__(self, container):
        self.data = container
        self.packages = {
            'Ubuntu 14.*': [
                'libvirt-bin',
                'qemu',
                'wget',
                'genisoimage',
            ],
            'CentOS Linux 7.*': [
                'epel-release',
                'libvirt',
                'virt-install',
                'qemu',
                'wget',
                'genisoimage',
            ],
        }
        self.services = [
            'libvirtd',
        ]
        # self.libvirt_dir = os.path.join(CONF._storage_dir, 'container', 'libvirt')
        self.libvirt_dir = os.path.join('/opt/fabkit', 'container', 'libvirt')
        self.template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.instances_dir = os.path.join(self.libvirt_dir, 'instances')
        filer.mkdir(self.instances_dir)
        self.pdns = pdnsapi.PdnsAPI()

    def create(self):
        data = self.data
        sudo('modprobe kvm')
        sudo('modprobe kvm_intel')

        network = CONF.network.libvirt_net.split(':')
        bridge = network[0]
        brctl_show = sudo('brctl show')
        if brctl_show.find(bridge) == -1:
            sudo('brctl addbr {0}'.format(bridge))

        ip_network = IPNetwork(network[1])
        gateway_ip = '{0}/{1}'.format(ip_network.ip + 1, ip_network.prefixlen)
        dhcp_ip = '{0}/{1}'.format(ip_network.ip + 2, ip_network.prefixlen)
        bridge_info = sudo('ip addr show dev {0}'.format(bridge))
        if bridge_info.find(gateway_ip) == -1:
            sudo('ip addr add {0} dev {1}'.format(gateway_ip, bridge))
        if bridge_info.find('DOWN') != -1:
            sudo('ip link set {0} up'.format(bridge))
            sudo('ip route add 10.0.0.0/8 via {0}'.format(ip_network.ip + 1))

        network_seg = "{0}/{1}".format(ip_network.ip, ip_network.netmask)

        ip_netns = sudo('ip netns show')
        dhcp_netns = 'dhcp-{0}'.format(bridge)
        dhcp_veth_br = 'ns-{0}'.format(bridge)
        dhcp_veth = 'veth-{0}'.format(bridge)
        if ip_netns.find(dhcp_netns):
            sudo('ip netns add {0}'.format(dhcp_netns))

        if brctl_show.find(dhcp_veth_br) == -1:
            sudo('ip link add {0} type veth peer name {1}'.format(dhcp_veth_br, dhcp_veth))
            sudo('brctl addif {0} {1}'.format(bridge, dhcp_veth_br))
            sudo('ip link set {0} up'.format(dhcp_veth_br))
            sudo('ip link set {0} netns {1}'.format(dhcp_veth, dhcp_netns))
            sudo('ip netns exec {0} ip addr add dev {1} {2}'.format(dhcp_netns, dhcp_veth, dhcp_ip))
            sudo('ip netns exec {0} ip link set {1} up'.format(dhcp_netns, dhcp_veth))

        # ss_ln = sudo('ip netns exec {0} ss -ln'.format(dhcp_netns))
        # if ss_ln.find('*:67') == -1:
        #     sudo('ip netns exec {0} dnsmasq -p 0 --dhcp-range 172.16.100.3,172.16.100.254,12h'.format(  # noqa
        #         dhcp_netns, ip_network[3], ip_network[-2]))
        ss_ln = sudo('ss -ln'.format(dhcp_netns))
        if ss_ln.find('*:67') == -1:
            sudo('dnsmasq -p 0 --dhcp-range=172.16.100.3,172.16.100.254')

        for i, vm in enumerate(data['libvirt_vms']):
            instance_dir = os.path.join(self.instances_dir, vm['name'])
            filer.mkdir(instance_dir)

            vm['bridge'] = bridge
            vm['hostname'] = '{0}.{1}'.format(vm['name'], CONF.network.domain)

            image_path = '{0}/vm.img'.format(instance_dir)
            vm['image_path'] = image_path
            src_image_path = self.wget_src_image(vm)
            if not filer.exists(image_path):
                sudo('cp {0} {1}'.format(src_image_path, image_path))
                sudo('qemu-img resize {0} {1}G'.format(image_path, vm.get('disk_size', 10)))
            if 'disk_cache' not in vm:
                vm['disk_cache'] = 'none'
            elif vm['disk_cache'] not in ['none', 'writethrough', 'writeback',
                                          'directsync', 'unsafe', 'default']:
                raise Exception('Invalid disk_cache: {0}'.format(vm['disk_cache']))

            configiso_path = self.create_configiso(vm, instance_dir)
            vm['configiso_path'] = configiso_path

            alias_index = 0
            pci_slot_num = 2
            for port in vm['ports']:
                mac = self.get_random_mac()
                port['mac'] = mac
                port['tap'] = 'tap{0}'.format(mac.replace(':', ''))

                port['pci_slot'] = '0x0{0}'.format(pci_slot_num)
                pci_slot_num += 1

                port['alias_name'] = 'net{0}'.format(alias_index)
                alias_index += 1

            vm['memballoon'] = {
                'pci_slot': '0x0{0}'.format(pci_slot_num)
            }

            domain_xml = self.create_domain_xml(vm, instance_dir)

            sudo("sed -i 's/^Defaults.*requiretty/# Defaults requiretty/' /etc/sudoers")

            for port in vm['ports']:
                if port['ip'] == 'none':
                    continue

                # sudo("virsh net-update {3} add ip-dhcp-host "
                #      "\"<host mac='{0}' name='{1}' ip='{2}' />\"".format(
                #          port['mac'], vm['name'], port['ip'], bridge))

            sudo('virsh define {0}'.format(domain_xml))
            sudo('chown -R root:root {0}'.format(instance_dir))
            sudo('virsh start {0}'.format(vm['name']))

        nat_table = sudo("iptables -t nat -L")
        if nat_table.find(network_seg) == -1:
            # sudo("iptables -R FORWARD 1 -o {0} -s {1}"
            #      " -d 0.0.0.0/0 -j ACCEPT".format(bridge, network_seg))
            sudo("iptables -t filter -A FORWARD -s 0.0.0.0/0 -d {0} -j ACCEPT".format(network_seg))
            sudo("iptables -t filter -A FORWARD -d 0.0.0.0/0 -s {0} -j ACCEPT".format(network_seg))

        nat_table = sudo("iptables -t nat -L")
        if nat_table.find(network_seg) == -1:
            sudo("iptables -t nat -A POSTROUTING -p TCP -s {0} ! -d {0} -j MASQUERADE --to-ports 1024-65535".format(
                network_seg))
            sudo("iptables -t nat -A POSTROUTING -p UDP -s {0} ! -d {0} -j MASQUERADE --to-ports 1024-65535".format(
                network_seg))
            sudo("iptables -t nat -A POSTROUTING -s {0} ! -d {0} -j MASQUERADE".format(
                network_seg))
            sudo("iptables -t nat -A POSTROUTING -s {0} -d 255.255.255.255 -j RETURN".format(
                network_seg))
            sudo("iptables -t nat -A POSTROUTING -s {0} -d base-address.mcast.net/24 -j RETURN".format(
                network_seg))

        for vm in data['libvirt_vms']:
            self.pdns.create_record(vm['name'], CONF.network.domain, 'A', vm['ports'][0]['ip'])

            while True:
                with api.warn_only():
                    if run('nmap -p 22 {0} | grep open'.format(vm['ports'][0]['ip'])):
                        break
                    time.sleep(5)

        for ip in data.get('iptables', {}):
            for port in ip.get('ports', []):
                if ip['ip'] == 'none':
                    continue
                sudo("iptables -t nat -A PREROUTING -p tcp"
                     " --dport {0[1]} -j DNAT --to {1}:{0[0]}".format(
                         port, ip['ip']))

        time.sleep(60)

    def delete(self):
        data = self.data
        for i, vm in enumerate(data['libvirt_vms']):
            with api.warn_only():
                self.pdns.delete_record('{0}.{1}'.format(vm['name'], CONF.network.domain))
                for port in vm['ports']:
                    if port['ip'] == 'none':
                        continue

                if sudo('virsh list | grep {0}'.format(vm['name'])).return_code == 0:
                    sudo('virsh destroy {0}'.format(vm['name']))
                if sudo('virsh list --all | grep {0}'.format(vm['name'])).return_code == 0:
                    sudo('virsh undefine {0}'.format(vm['name']))

            instance_dir = os.path.join(self.instances_dir, vm['name'])
            sudo('rm -rf {0}'.format(instance_dir))

    def stop(self):
        pass

    def start(self):
        pass

    def restart(self):
        self.stop()
        self.start()

    def wget_src_image(self, vm):
        images_dir = os.path.join(self.libvirt_dir, 'images')
        filer.mkdir(images_dir)

        src_image = vm['src_image'].rsplit('/', 1)[1]
        src_image_path = '{0}/{1}'.format(images_dir, src_image)
        src_image_format = 'qcow2'

        if src_image_path[-3:] == '.xz':
            src_image_path = src_image_path[:-3]
            src_image_format = 'xz'

        if not filer.exists(src_image_path):
            sudo('sh -c "cd {0} && wget {1}"'.format(images_dir, vm['src_image']))

            if src_image_format == 'xz':
                sudo('sh -c "cd {0} && xz -d {1}"'.format(images_dir, src_image))

        return src_image_path

    def create_configiso(self, vm, instance_dir):
        data = self.data

        template_data = {
            'user': CONF.job_user,
            'password': CONF.job_password,
            'vm': vm,
            'gateway': data['libvirt']['gateway'],
            'netmask': data['libvirt']['netmask'],
        }

        metadata_path = '{0}/meta-data'.format(instance_dir)
        userdata_path = '{0}/user-data'.format(instance_dir)
        configiso_path = '{0}/config.iso'.format(instance_dir)

        src_metadata_path = os.path.join(self.template_dir, 'meta-data')
        src_userdata_path = os.path.join(self.template_dir, vm['template'])
        filer.template(metadata_path, src_file=src_metadata_path, data=template_data)
        filer.template(userdata_path, src_file=src_userdata_path, data=template_data)
        if not filer.exists(configiso_path):
            sudo('genisoimage -o {0} -V cidata -r -J {1} {2}'.format(
                configiso_path, metadata_path, userdata_path))

        return configiso_path

    def create_domain_xml(self, vm, instance_dir):
        vm['uuid'] = str(uuid.uuid1())

        domain_xml = '{0}/domain.xml'.format(instance_dir)
        src_domain_xml = os.path.join(self.template_dir, 'domain.xml')
        filer.template(domain_xml, src_file=src_domain_xml, data=vm)
        return domain_xml

    def get_random_mac(self):
        mac = [0x00, 0x16, 0x3e,
               random.randint(0x00, 0x7f),
               random.randint(0x00, 0xff),
               random.randint(0x00, 0xff)]

        return ':'.join(map(lambda x: "%02x" % x, mac))
