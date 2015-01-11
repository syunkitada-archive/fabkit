# coding: utf-8

import json
import platform
import getpass
from fabric.api import (env,
                        task,
                        hosts,)
from lib import util
from lib.api import *  # noqa
from types import StringType


@task
@hosts('localhost')
def chefnode(option=None, host=None, chefoption=''):
    if option == 'bootstrap':
        host = __check_to_enter_host(host)
        env.hosts = util.get_expanded_hosts(host)
        if len(env.hosts) == 0:
            print 'Empty nodes'
            return

        print env.hosts
        print 'option: {0}'.format(chefoption)

        # knife bootstrap `hostname` -A -x owner --sudo -r 'recipe[cookbook-test]'
        # knife node run_list add 192.168.33.10 recipe[cookbook-test]

        if util.confirm('Are you sure you want to bootstrap above nodes?', 'Canceled'):
            for host in env.hosts:
                cmd_bootstrap = 'knife bootstrap {0} -x {1} -N {0} --sudo {2}'.format(host, env.user, chefoption)  # noqa
                local(cmd_bootstrap)

        return
    else:
        env.is_chef = True
        if not option:
            host = '*'
        else:
            host = option

        option = host
        search_cmd = 'knife search node "name:{0}" -F json'.format(host)
        searched_nodes = cmd(search_cmd)[1]
        if env.is_test:
            nodes = [{'name': host}]
        else:
            nodes = json.loads(searched_nodes)['rows']

        for node in nodes:
            node.update(util.load_node(node['name']))
            node.update({'path': node['name']})
            env.node_map.update({node['name']: node})

        util.print_node_map(option=option)
        check_continue()


@task
@hosts('localhost')
def node(option=None, host=None, edit_key=None, *edit_value):
    env.is_chef = False

    if option == 'create':
        host = __check_to_enter_host(host)
        hosts = util.get_expanded_hosts(host)

        for host in hosts:
            print host

        if util.confirm('Are you sure you want to create above nodes?', 'Canceled'):
            for host in hosts:
                util.dump_node(host[0], is_init=True)
                if edit_key and edit_value:
                    node = util.load_node(host[0])
                    node.update({edit_key: __convert_value(edit_key, edit_value, host[1])})
                    util.dump_node(host, node)

        util.load_node_map(host)
        util.print_node_map()

        return

    elif option == 'remove':
        host = __check_to_enter_host(host)
        hosts = util.get_available_hosts(host)
        if len(hosts) == 0:
            print 'Empty hosts.'
            return

        print hosts
        if util.confirm('Are you sure you want to remove above nodes?', 'Canceled'):
            for host in hosts:
                util.remove_node(host)

            print '{0} removed.'.format(host)

        return

    elif option == 'edit':
        host = __check_to_enter_host(host)
        util.load_node_map(host)
        util.print_node_map()

        print '\n\nEdit above nodes.'
        node_keys = ['fabruns', 'attrs']
        if not edit_key:
            while True:
                edit_key = raw_input('Enter key: ')
                if edit_key in node_keys:
                    break
                else:
                    print 'This key is not available'

        if not edit_value:
            edit_value = raw_input('Enter value: ')

        edit_value = __convert_value(edit_key, edit_value)

        for node in env.node_map.values():
            node.update({edit_key: edit_value})
            util.dump_node(node['path'], node)

        util.print_node_map()
        check_continue()

        return

    elif option == 'resent':
        print 'resent'

    elif option == 'error':
        print 'errors'

    else:
        # optionなし、もしくは、vの場合は、hostは*ワイルドカードとなる
        if not option:
            host = '*'
            print_option = None
        elif option == 'v':
            host = '*'
            print_option = 'v'
        else:
            # node:host,option の形式となるように引数を調整
            host = option
            print_option = host

        util.load_node_map(host)
        util.print_node_map(option=print_option)
        check_continue()

        return


def check_continue():
    if len(env.hosts) == 0:
        print('Empty hosts.')
        return

    is_setup = False
    is_manage = False

    for task_name in env.tasks:
        if not is_setup:
            is_setup = task_name.find('setup') == 0
        if not is_manage:
            is_setup = task_name.find('manage') == 0

    if len(env.tasks) > 1:
        if util.confirm('Are you sure you want to run task on above nodes?', 'Canceled'):
            if (is_setup or is_manage) and not env.password:
                print 'Enter your password.\n'
                if platform.system().find('CYGWIN') == 0:
                    env.password = getpass.getpass()
                else:
                    sudo('hostname')
        else:
            env.hosts = []
            exit()


def __check_to_enter_host(host):
    ''' hostが入力されているかチェックする
    hostが入力されていなければ、ユーザに入力を求める
    '''
    while not host or host == '':
        host = raw_input('Please enter host: ')
    return host


def __convert_value(key, value, fragments):
    if key == 'fabruns':
        if type(value) is StringType:
            value = value.split(',')

        result = []
        for v in value:
            result.append(v.format(*fragments))

        return result

    else:
        return value
