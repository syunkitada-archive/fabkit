# coding: utf-8

from fabric.api import env, task, hosts, cd
import re, os, json, sys
from types import *
import datetime
import util, conf, testtools
from api import *

@task
@hosts('localhost')
def node(option=None, host_pattern=None, edit_key=None, edit_value=None):
    if option == 'create':
        host_pattern = check_host_pattern(host_pattern)
        env.hosts = util.get_expanded_hosts(host_pattern)
        print env.hosts

        if util.confirm('Are you sure you want to create above nodes?', 'Canceled'):
            for host in env.hosts:
                if not util.exists_json(host):
                    util.dump_json(conf.get_initial_json(host), host)
                else:
                    print '{0} is already created.'.format(host)
            print_hosts()

        return

    elif option == 'remove':
        host_pattern = check_host_pattern(host_pattern)
        env.hosts = util.get_available_hosts(host_pattern)
        print env.hosts

        if util.confirm('Are you sure you want to remove above nodes?', 'Canceled'):
            for host in env.hosts:
                util.remove_json(host)

            print '{0} removed.'.format(host_pattern)

        return

    elif option == 'edit':
        host_pattern = check_host_pattern(host_pattern)
        env.hosts = util.get_available_hosts(host_pattern)
        print_hosts()

        print '\n\nEdit above nodes.'
        if not edit_key and type(edit_value) is not StringType:
            edit_key = raw_input('Enter key: ')

        if not edit_value and type(edit_value) is not StringType:
            edit_value = raw_input('Enter value: ')

        for host in env.hosts:
            host_json = util.load_json(host)
            host_json.update({edit_key: edit_value})
            util.dump_json(host_json, host)

        print_hosts()

    elif option == 'upload':
        host_pattern = check_host_pattern(host_pattern)
        env.hosts = util.get_available_hosts(host_pattern)
        print_hosts()

        if util.confirm('Are you sure you want to upload above nodes?', 'Canceled'):
            for host in env.hosts:
                if util.exists_json(host):
                    print cmd('knife node from file {0}/{1}.json'.format(conf.NODE_DIR, host))[1]
        return

    elif option == 'download':
        host_pattern = check_host_pattern(host_pattern)
        searched_nodes = cmd('knife search node "name:{0}" -F json'.format(host_pattern))[1]
        if env.is_test:
            searched_nodes = testtools.get_searched_nodes(host_pattern)

        nodes = json.loads(searched_nodes)['rows']
        for node in nodes:
            print node['name']

        if util.confirm('Are you sure you want to save above nodes?', 'Canceled'):
            for node in nodes:
                host = node['name']
                node_json = util.load_json(host)
                node_json.update(node)
                util.dump_json(node_json, host)
                print 'saved {0}'.format(host)

        return

    elif option == 'check':
        warning_nodes    = cmd('grep \' \[.*[^0]\]\' -r {0}/*'.format(conf.NODE_DIR))[1]
        failed_ssh_nodes = cmd('grep \'"ssh": "failed"\' -r {0}/*'.format(conf.NODE_DIR))[1]
        if warning_nodes == '' and failed_ssh_nodes == '':
            print 'No warning nodes.'
        else:
            print warning_nodes
            print failed_ssh_nodes

        return

    else:
        if option == 's':
            env.is_server = True
            searched_nodes = cmd('knife search node "name:{0}" -F json'.format(host_pattern))[1]
            if env.is_test:
                searched_nodes = testtools.get_searched_nodes(host_pattern)

            nodes = json.loads(searched_nodes)['rows']
            hosts = []
            for node in nodes:
                print '{0:<40} {1}'.format(node['name'], node['run_list'])
                hosts.append(node['name'])
            env.hosts = hosts

        else:
            is_verbose = False
            if option:
                if host_pattern == 'v':
                    is_verbose = True
                host_pattern = option
            else:
                host_pattern = '*'

            env.hosts = util.get_available_hosts(host_pattern)
            print_hosts(is_verbose)

        RE_ROLE = re.compile('role\[(.+)\]')
        for host in env.hosts:
            host_json = util.load_json(host)
            for run_list in host_json['run_list']:
                role = RE_ROLE.match(run_list)
                if role:
                    role_name = role.group(1)
                    role_hosts = env.roledefs.get(role_name, [])
                    role_hosts.append(host)
                    env.roledefs.update({
                        role_name: role_hosts
                    })

        for task in env.tasks:
            is_prepare = task.find('prepare') == 0
            is_cook = task.find('cook') == 0

            if is_prepare or is_cook:
                if util.confirm('Are you sure you want to run task that follow on above nodes?', 'Canceled'):
                    print 'enter your password\n'
                    sudo('hostname')
                else:
                    env.hosts = []
                    return

                if is_cook:
                    if not conf.is_server(task[4:]):
                        set_pass(conf.UUID, env.password)
                        # knife solo 使わなくてもできるかも
                        local('cd {0} && knife solo cook localhost --no-berkshelf --no-chef-check --ssh-password {1}'.format(conf.CHEFREPO_DIR, get_pass(conf.UUID)))
                        run('tar -czf chef-solo.tar.gz chef-solo')
                        unset_pass()

def check_host_pattern(host_pattern):
    while not host_pattern or host_pattern == '':
        host_pattern = raw_input('Please enter host: ')
    return host_pattern

RE_UPTIME = re.compile('^.*up (.+),.*user.*$')
def print_hosts(is_verbose=False):
    if not is_verbose:
        format_str = '{hostname:<40} {run_list} {fab_run_list}'
        print '----------------------------------------------------------------------'
        print format_str.format(
                hostname = 'hostname',
                run_list = 'run_list',
                fab_run_list = 'fab_run_list',
                )
    else:
        format_str = '''\
host_info     : {host_info}
uptime        : {uptime}
run_list      : {run_list}
last_cook     : {last_cook}
fab_run_list  : {fab_run_list}
last_fabcooks : {last_fabcooks}
last_check    : {last_check}
        '''

    print '----------------------------------------------------------------------'

    for host in env.hosts:
        host_json = util.load_json(host)
        run_list = host_json.get('run_list', [])
        fab_run_list = host_json.get('fab_run_list', [])

        if not is_verbose:
            print format_str.format(
                    hostname = host,
                    run_list = run_list,
                    fab_run_list = fab_run_list,
                )
        else:
            host_info = '{0}({1}) ssh:{2}'.format(host, host_json.get('ipaddress', ''), host_json.get('ssh'))
            uptime = host_json.get('uptime', '')
            last_cook = host_json.get('last_cook', '')
            last_fabcooks = host_json.get('last_fabcooks', [])
            last_check = host_json.get('last_check', '')
            print format_str.format(
                    host_info = host_info,
                    run_list = run_list,
                    fab_run_list = fab_run_list,
                    uptime = uptime,
                    last_cook = last_cook,
                    last_fabcooks = last_fabcooks,
                    last_check = last_check,
                )


