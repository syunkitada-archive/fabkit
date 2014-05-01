from fabric.api import env, task, hosts, cd
import re, os, json, sys
from types import *
import datetime
import util, conf, testtools
from api import *

RE_UPTIME = re.compile('^.*up (.+),.*user.*$')

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
                    print '%s is already created.' % host
            print_hosts()

        return

    elif option == 'remove':
        host_pattern = check_host_pattern(host_pattern)
        env.hosts = util.get_available_hosts(host_pattern)
        print env.hosts

        if util.confirm('Are you sure you want to remove above nodes?', 'Canceled'):
            for host in env.hosts:
                util.remove_json(host)

            print '%s removed.' % host_pattern

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
                    print cmd('knife node from file %s/%s.json' % (conf.node_path, host))
        return

    elif option == 'download':
        host_pattern = check_host_pattern(host_pattern)
        searched_nodes = cmd('knife search node "name:%s" -F json' % host_pattern)
        if env.is_test:
            searched_nodes = testtools.get_searched_nodes(host_pattern)

        print searched_nodes

        if util.confirm('Are you sure you want to save above nodes?', 'Canceled'):
            nodes = json.loads(searched_nodes)['rows']
            for node in nodes:
                host = node['name']
                node_json = util.load_json(host)
                node_json.update(node)
                util.dump_json(node_json, host)
                print host

            print '\nsaved %s\n' % host_pattern
            env.hosts = util.get_available_hosts(host_pattern)
            print_hosts()
        return

    else:
        if option:
            host_pattern = option
        else:
            host_pattern = '*'

        env.hosts = util.get_available_hosts(host_pattern)
        print_hosts()

        for task in env.tasks:
            is_prepare = task.find('prapare') != -1
            is_cook = task.find('cook') != -1

            if is_prepare or is_cook:
                if util.confirm('Are you sure you want to run task that follow on above nodes?', 'Canceled'):
                    print 'enter your password\n'
                    sudo('hostname')
                else:
                    return

                if is_cook:
                    if not conf.is_server(task[4:]):
                        os.environ['PASSWORD'] = env.password
                        local('cd %s && knife solo cook localhost --no-berkshelf --no-chef-check --ssh-password $PASSWORD' % conf.chef_repo_path)
                        run('cp -r %s/* chef-solo/' % conf.node_path)
                        run('tar -czf chef-solo.tar.gz chef-solo')
                        os.environ['PASSWORD'] = ''


def check_host_pattern(host_pattern):
    while not host_pattern or host_pattern == '':
        host_pattern = raw_input('Please enter host: ')
    return host_pattern

def print_hosts():
    host = 'hostname'
    uptime = 'uptime'
    last_cook = 'last_cook'
    run_list = 'run_list'
    print '%(host)-40s%(uptime)-15s%(last_cook)-25s%(run_list)s' % locals()
    print '-------------------------------------------------------------------------------------------'

    for host in env.hosts:
        host_json = util.load_json(host)

        uptime = host_json.get('uptime', '')
        uptimes = RE_UPTIME.search(uptime)
        if uptimes:
            uptime = uptimes.group(1)
        last_cook = host_json.get('last_cook')
        run_list = host_json.get('run_list')

        print '%(host)-40s%(uptime)-15s%(last_cook)-25s%(run_list)s' % locals()


