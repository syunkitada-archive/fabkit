# Task setup


Run task function that begins with setup of fabscript.

## Args
* test
  * run in test mode.

## Examples
```
% fab node:test/api setup
[localhost] Executing task 'node'
-----------------------------------------------
cluster host       fabscript
-----------------------------------------------
test    api01.host test/api: 0 > 0
...
...
[api01.host] INFO: Success task test/api.setup [0]. success
```
