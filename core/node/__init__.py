# coding: utf-8

import platform
import getpass
from fabkit import api, env, db, util, sudo, status_code
from types import StringType


@api.task
@api.hosts('localhost')
def node(*options):
    len_options = len(options)

    if len_options == 0 or options[0] in ['recent', 're', 'error', 'er']:
        length = int(options[1]) if len_options > 1 else None
        if len_options == 0 or options[0] in ['recent', 're']:
            nodes = db.get_recent_nodes(length)
        else:
            nodes = db.get_error_nodes(length)

        for node in nodes:
            util.load_node(node.path)

        util.print_node_map(option='status')
        exit(0)

    elif options[0] in ['create', 'c']:
        host = __check_to_enter_host(options, 1)
        hosts = util.get_expanded_hosts(host)

        edit_key = 'fabruns'
        for tmp_host in hosts:
            if len_options > 2:
                edit_value = options[2]
                node = util.load_node(tmp_host[0])
                print '{0} {1}'.format(tmp_host, __convert_value(edit_key, edit_value, tmp_host[1]))
            else:
                print tmp_host

        if util.confirm('Are you sure you want to create above nodes?', 'Canceled'):
            for tmp_host in hosts:
                util.dump_node(tmp_host[0], is_init=True)
                if len_options > 2:
                    edit_value = options[2]
                    node = util.load_node(tmp_host[0])
                    node.update({edit_key: __convert_value(edit_key, edit_value, tmp_host[1])})
                    util.dump_node(tmp_host[0], node)

        util.load_node_map(host)
        util.print_node_map()

        exit(0)

    elif options[0] in ['remove', 'r']:
        host = __check_to_enter_host(options, 1)
        hosts = util.get_available_hosts(host)
        if len(hosts) == 0:
            print 'Empty hosts.'
            return

        for tmp_host in hosts:
            print tmp_host

        if util.confirm('Are you sure you want to remove above nodes?', 'Canceled'):
            for tmp_host in hosts:
                util.remove_node(tmp_host)
                print '{0} removed.'.format(tmp_host)

        exit(0)

    elif options[0] in ['edit', 'e']:
        host = __check_to_enter_host(options, 1)
        util.load_node_map(host)
        util.print_node_map()

        print '\n\nEdit above nodes.'
        node_keys = ['fabruns', 'attrs']
        if len(options) > 2:
            edit_key = options[2]
        else:
            while True:
                edit_key = raw_input('Enter key: ')
                if edit_key in node_keys:
                    break
                else:
                    print 'This key is not available'

        if len(options) > 3:
            edit_value = options[3]
        else:
            edit_value = raw_input('Enter value: ')

        edit_value = __convert_value(edit_key, edit_value, [])

        for node in env.node_map.values():
            node.update({edit_key: edit_value})
            util.dump_node(node['path'], node)

        util.print_node_map()

        exit(0)

    else:
        host = options[0]
        print_option = options[1] if len_options > 1 else None

        util.load_node_map(host)
        util.print_node_map(option=print_option)

        # オプションがないときだけ、続行する
        if print_option is not None:
            exit(0)

        check_continue()


@api.task
@api.hosts('localhost')
def dump(option=None, host=None, chefoption=''):
    util.print_node_map(option='status')


def check_continue():
    if len(env.hosts) == 0:
        print('Empty hosts.')
        return

    is_setup = False
    is_manage = False
    is_check = False

    for task_name in env.tasks:
        if not is_setup:
            is_setup = task_name.find('setup') == 0
        if not is_manage:
            is_manage = task_name.find('manage') == 0
        if not is_check:
            is_check = task_name.find('check') == 0

    if len(env.tasks) > 1:
        if util.confirm('Are you sure you want to run task on above nodes?', 'Canceled'):
            if (is_setup or is_manage or is_check) and (not env.password or env.password == ''):
                print 'Enter your password.\n'
                if platform.system().find('CYGWIN') == 0:
                    env.password = getpass.getpass()
                else:
                    sudo('hostname')

            for node in env.node_map:
                db.setuped(status_code.FABSCRIPT_REGISTERED, 'registered', host=node)

            # Djangodbのコネクションをリセットしておく
            # これをやらないと、タスクをまたいでdbにアクセスした時に、IO ERRORとなる
            from django import db as djangodb
            djangodb.close_old_connections()

        else:
            env.hosts = []
            exit()


def __check_to_enter_host(options, index):
    if len(options) <= index or options[index] == '':
        host = raw_input('Please enter host: ')
    else:
        host = options[index]
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
