# coding: utf-8

from base import setup, check, manage, job

setup.__doc__ = """
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
"""

check.__doc__ = """
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
"""

manage.__doc__ = """
Run task function that match input pattern of fabscript.

## Args
* [pattern]
  * run task function that match input <pattern>
* test,[pattern]
  * run in test mode.
* help
  * show all help of task function.
* help,[pattern]
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
"""

job.__doc__ = """
Start Job.

## Examples
```
% fab node:test/api job
```
"""
