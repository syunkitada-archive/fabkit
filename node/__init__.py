# coding: utf-8

import re
import json
from fabric.api import (env,
                        task,
                        hosts,)
import util
import conf
import testtools
from api import *  # noqa

RE_UPTIME = re.compile('^.*up (.+),.*user.*$')


@task
@hosts('localhost')
def chefnode(option=None, host_pattern=None):
    if option == 'bootstrap':
        host_pattern = check_host_pattern(host_pattern)
        env.hosts = util.get_expanded_hosts(host_pattern)
        if len(env.hosts) == 0:
            print 'Empty nodes'
            return

        print env.hosts

        if util.confirm('Are you sure you want to create above nodes?', 'Canceled'):
            for host in env.hosts:
                print '{0} host.'.format(host)
                cmd_bootstrap = 'knife bootstrap {0} -x {1} -N {0} --sudo'.format(host, env.user)  # noqa
                print cmd_bootstrap
                local(cmd_bootstrap)

        return
    else:
        # knife bootstrap `hostname` -A -x owner --sudo -r 'recipe[cookbook-test]'
        # knife node run_list add 192.168.33.10 recipe[cookbook-test]

        env.is_chef = True
        if not option:
            host_name = '*'
        else:
            host_name = option

        option = host_pattern
        searched_nodes = cmd('knife search node "name:{0}" -F json'.format(host_name))[1]
        if env.is_test:
            searched_nodes = testtools.get_searched_nodes(host_name)

        nodes = json.loads(searched_nodes)['rows']
        if option == 'v':
            for node in nodes:
                node.update(util.load_json(node['name']))

        print_nodes(nodes, option)
        check_continue()


@task
@hosts('localhost')
def node(option=None, host_pattern=None, edit_key=None, edit_value=None):
    env.is_chef = False

    if option == 'create':
        host_pattern = check_host_pattern(host_pattern)
        env.hosts = util.get_expanded_hosts(host_pattern)
        if len(env.hosts) == 0:
            print 'Empty nodes'
            return

        print env.hosts

        if util.confirm('Are you sure you want to create above nodes?', 'Canceled'):
            for host in env.hosts:
                if not util.exists_json(host):
                    util.dump_json(conf.get_initial_json(host), host)
                else:
                    print '{0} is already created.'.format(host)

            set_hosts(host_pattern)
            check_continue()

        return

    elif option == 'remove':
        host_pattern = check_host_pattern(host_pattern)
        hosts = util.get_available_hosts(host_pattern)
        if len(hosts) == 0:
            print 'Empty hosts.'
            return

        print hosts
        if util.confirm('Are you sure you want to remove above nodes?', 'Canceled'):
            for host in hosts:
                util.remove_json(host)

            print '{0} removed.'.format(host_pattern)

        return

    elif option == 'edit':
        host_pattern = check_host_pattern(host_pattern)
        set_hosts(host_pattern)

        print '\n\nEdit above nodes.'
        if not edit_key and type(edit_value) is not StringType:
            edit_key = raw_input('Enter key: ')

        if not edit_value and type(edit_value) is not StringType:
            edit_value = raw_input('Enter value: ')

        for host in env.hosts:
            host_json = util.load_json(host)
            host_json.update({edit_key: edit_value})
            util.dump_json(host_json, host)

        set_hosts(host_pattern)
        check_continue()

        return

    else:
        # optionなしの場合、optionがhost_patternの役割をはたし、host_patternがoptionになる
        if not option:
            option = '*'
        set_hosts(option, host_pattern)
        check_continue()


def set_hosts(host_pattern='*', option=None):
    hosts = util.get_available_hosts(host_pattern)
    nodes = []
    for host in hosts:
        nodes.append(util.load_json(host))

    print_nodes(nodes, option)


def check_host_pattern(host_pattern):
    while not host_pattern or host_pattern == '':
        host_pattern = raw_input('Please enter host: ')
    return host_pattern


def check_continue():
    if len(env.hosts) == 0:
        print('Empty hosts.')
        return

    is_cook = False
    is_prepare = False

    for task_name in env.tasks:
        if not is_cook:
            is_cook = task_name.find('cook') == 0
        if not is_prepare:
            is_prepare = task_name.find('prepare') == 0

    if len(env.tasks) > 1:
        if util.confirm('Are you sure you want to run task on above nodes?', 'Canceled'):
            if is_prepare or is_cook:
                print 'Enter your password.\n'
                sudo('hostname')
        else:
            env.hosts = []
            exit()


def print_nodes(nodes=[], option=''):
    is_verbose = False
    if option is not None and option.find('v') > -1:
        is_verbose = True

    if not is_verbose:
        if len(nodes) == 0:
            max_len_hostname = 10
        else:
            max_len_hostname = max([len(node['name']) for node in nodes])
        if env.is_chef:
            format_str = '{hostname:<' + str(max_len_hostname) + '} {run_list}'
            horizontal_line = '-' * (max_len_hostname + 30)
        else:
            format_str = '{hostname:<' + str(max_len_hostname) + '} {fab_run_list}'
            horizontal_line = '-' * (max_len_hostname + 50)

        print horizontal_line
        print format_str.format(hostname='hostname',
                                run_list='run_list',
                                fab_run_list='fab_run_list',)
        print horizontal_line

    else:
        if env.is_chef:
            format_str = '''\
host_info     : {host_info}
uptime        : {uptime}
environment   : {environment}
run_list      : {run_list}
last_cook     : {last_cook}
last_check    : {last_check}
'''
        else:
            format_str = '''\
host_info     : {host_info}
uptime        : {uptime}
fab_run_list  : {fab_run_list}
last_fabcooks : {last_fabcooks}
last_check    : {last_check}
'''
            horizontal_line = '-' * 85
            print horizontal_line
            format_str += horizontal_line

    nodes = sorted(nodes, key=lambda node: str(node['name']), reverse=False)
    env_hosts = []
    for node in nodes:
        hostname = node.get('name', '')
        env_hosts.append(hostname)
        run_list = node.get('run_list', [])
        fab_run_list = node.get('fab_run_list', [])

        if not is_verbose:
            print format_str.format(hostname=hostname,
                                    run_list=run_list,
                                    fab_run_list=fab_run_list,)
        else:
            host_info = '{0}({1}) ssh:{2}'.format(hostname,
                                                  node.get('ipaddress', ''), node.get('ssh'))
            uptime = node.get('uptime', '')
            environment = node.get('chef_environment', '')
            last_cook = node.get('last_cook', '')
            last_fabcooks = node.get('last_fabcooks', [])
            last_runs = node.get('last_runs', [])
            last_check = node.get('last_check', '')
            print format_str.format(environment=environment,
                                    host_info=host_info,
                                    run_list=run_list,
                                    fab_run_list=fab_run_list,
                                    uptime=uptime,
                                    last_cook=last_cook,
                                    last_fabcooks=last_fabcooks,
                                    last_runs=last_runs,
                                    last_check=last_check,)

    env.hosts = env_hosts
