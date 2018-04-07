# coding: utf-8

from base import node, nodestr  # noqa

node.__doc__ = """
Load node and cluster from yaml files in node_dir.

## Args
* [cluster_path/pattern],[find_depth]
  * load cluster and narrow down node from pattern.

## Examples
``` bash
% fab node:test/
[localhost] Executing task 'node'
-----------------------------------------------
cluster host       fabscript
-----------------------------------------------
test    api01.host test/api: 0 > 0
test    db01.host  test/db: 0 > 0
test    db02.host  test/db: 0 > 0

% fab node:test/api
[localhost] Executing task 'node'
-----------------------------------------------
cluster host       fabscript
-----------------------------------------------
test    api01.host test/api: 0 > 0

% fab node:test/api,2
[localhost] Executing task 'node'
-----------------------------------------------
cluster      host        fabscript
-----------------------------------------------
test         api01.host  test/api: 0 > 0
test/cluster capi01.host cluster/api: 0 > 0
```
"""


nodestr.__doc__ = """
Load node and cluster from string option.

## Args
* [host_pattern],[fabruns],[cluster_data={json}]
    * load hosts and fabruns
    * cluster_data is optional

## Examples
``` bash
# basic
$ fab nodestr:hoge-centos7-[1-3].example.com,test/helloworld setup
[localhost] Executing task 'nodestr'
--------------------------------------------------------------------------------------------------
cluster                         host                        fabscript
--------------------------------------------------------------------------------------------------
hoge-centos7-[1-3].example.com hoge-centos7-1.example.com test/helloworld: 0 > 0
hoge-centos7-[1-3].example.com hoge-centos7-2.example.com test/helloworld: 0 > 0
hoge-centos7-[1-3].example.com hoge-centos7-3.example.com test/helloworld: 0 > 0

Are you sure you want to run task on above nodes? (y/n) y
...


# show recent result
$ fab nodestr
[localhost] Executing task 'nodestr'
----------------------------------------
Cluster: hoge-centos7-[1-3].example.com

----------------------------------------
fabscript   status task_status
----------------------------------------
test/helloworld 0      0


--------------------------------------------------------------------------------
status     host                        fabscript
--------------------------------------------------------------------------------
-1         hoge-centos7-1.example.com test/helloworld:{'status': 0, 'msg': 'success', 'check_msg': '', 'task_status': 0, 'check_status': -1}
-1         hoge-centos7-2.example.com test/helloworld:{'status': 0, 'msg': 'success', 'check_msg': '', 'task_status': 0, 'check_status': -1}
-1         hoge-centos7-3.example.com test/helloworld:{'status': 0, 'msg': 'success', 'check_msg': '', 'task_status': 0, 'check_status': -1}
```
"""
