from fabric.api import *
import re, os, json, commands, sys
from types import *
import datetime
import util, conf

@task
def edit(host_pattern='*', edit_target=None, edit_value=None):
    if host_pattern == 'create':
        if not edit_target:
            edit_target = raw_input('enter hostname: ')

        for hostname in util.expand_hostname(edit_target):
            if not util.exists_json(hostname):
                util.dump_json(conf.template_json, hostname)
            else:
                print '%s is already created.' % hostname

        host_pattern = edit_target
        edit_target = None

    if host_pattern == 'remove':
        if not edit_target:
            edit_target = raw_input('enter hostname: ')
        for hostname in util.get_available_hosts(edit_target):
            util.remove_json(hostname)

        return

    hosts = util.get_available_hosts(host_pattern)

    host = 'hostname'
    uptime = 'uptime'
    last_cook = 'last_cook'
    run_list = 'run_list'
    print '%(host)-40s%(uptime)-15s%(last_cook)-25s%(run_list)s' % locals()
    print '-------------------------------------------------------------------------------------------'
    for host in hosts:
        path = '%s/%s.json' % (conf.node_path, host)
        with open(path, 'r') as f:
            host_json = json.load(f)
        ip_address = host_json.get('ip_address')
        uptime = host_json.get('uptime', '')
        prog = re.compile('^.*up (.+),.*user.*$')
        progs = prog.search(uptime)
        if progs:
            uptime = progs.group(1)
        last_cook = host_json.get('last_cook')
        run_list = host_json.get('run_list')
        print '%(host)-40s%(uptime)-15s%(last_cook)-25s%(run_list)s' % locals()

    if edit_target and type(edit_target) is StringType:
        if not edit_value and type(edit_value) is not StringType:
            print '\nedit "%s" of above nodes. if you leave, press ^C.' % edit_target
            edit_value = raw_input('enter value: ')

        for host in hosts:
            host_json = util.load_json(host)
            host_json.update({edit_target: edit_value})
            util.dump_json(host_json, host)

