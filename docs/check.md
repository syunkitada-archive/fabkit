# Task check


Run task function that begins with check of fabscript.

## Args
* test
  * run in test mode.

## Examples
```
% fab node:test/api check
[localhost] Executing task 'node'
-----------------------------------------------
cluster host       fabscript
-----------------------------------------------
test    api01.host test/api: 0 > 0
...
...
[api01.host] INFO: Success task test/api.check [0]. success
```
