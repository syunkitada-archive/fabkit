# Task manage


Run task function that match input pattern of fabscript.

## Args
* <pattern>
  * run task function that match input <pattern>
* test,<pattern>
  * run in test mode.
* help
  * show all help of task function.
* help,<pattern>
  * show help that match input <pattern> of task function.

## Examples
```
% fab node:test/api manage:restart
[localhost] Executing task 'node'
-----------------------------------------------
cluster host       fabscript
-----------------------------------------------
test    api01.host test/api: 0 > 0
...
...
[api01.host] INFO: Success task test/api.restart [0]. success

% fab node:test/api manage:help
[localhost] Executing task 'node'
-----------------------------------------------
cluster host       fabscript
-----------------------------------------------
test    api01.host test/api: 0 > 0

Task: setup

    document setup
    ...
```
