# coding: utf-8

from base import databag  # noqa

databag.__doc__ = """
Set key-value to databag, or show value or list.

## Args
* set(s),[databag.key],[value]
  * set key-value to databag.
* get(g),[databag.key]
  * get value from key.
* list(l),[databag]
  * show databag list
  * if not databag, show all databag list

## Examples
``` bash
% fab databag:s,test/database.password,dbpass
[localhost] Executing task 'databag'
set key:test/database.password, value:dbpass

% fab databag:g,test/database.password
[localhost] Executing task 'databag'
dbpass

% fab databag:l,test
[localhost] Executing task 'databag'
test/database

% fab databag:l
[localhost] Executing task 'databag'
test/database
test2/database
test3/database
...
```
"""
