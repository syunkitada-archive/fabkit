# Task node


Load node and cluster from yaml files in node_dir.

## Args
* <cluster_path/pattern>,<find_depth>
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
