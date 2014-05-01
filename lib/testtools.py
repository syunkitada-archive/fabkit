# coding: utf-8

# library for test

import os
from fabric.api import env
import commands
import util, conf
import json

# for test config
def init_conf():
    env.cmd_history = []
    conf.chef_repo_path = os.path.join(os.path.dirname(__file__), '../test/chef-repo')
    conf.node_path      = os.path.join(conf.chef_repo_path, 'node')
    conf.role_path      = os.path.join(conf.chef_repo_path, 'role')
    conf.chef_rpm_path  = os.path.join(conf.chef_repo_path, 'test-chef.rpm')
    conf.log_dir_path   = '/tmp/chef-testlog'
    conf.http_proxy     = 'test.proxy'
    conf.https_proxy    = 'test.proxy'

    if not os.path.exists(conf.log_dir_path):
        os.mkdir(conf.log_dir_path)

def get_searched_nodes_obj(host_pattern):
    hosts = []
    for host in util.get_expanded_hosts(host_pattern):
        hosts.append({
                "name": host,
                "chef_environment": "_default",
                "json_class": "Chef::Node",
                "automatic": {},
                "normal": {},
                "chef_type": "node",
                "default": {},
                "override": {},
                "run_list": [ "" ]
            })

    return { "results": len(hosts), "rows": hosts }


def get_searched_nodes(host_pattern):
    return json.dumps(get_searched_nodes_obj(host_pattern))
