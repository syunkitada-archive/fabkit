# coding: utf-8

from base import databag  # noqa

databag.__doc__ = """
access databag

## Args
* option (str): action option
  * set(s),[databag.key],[value]
    * set databag
  * get(g),[databag.key]
    * get databag
  * list(l),[databag]
    * show databag list
    * if not databag, show all databag list

## Examples
``` bash
$ fab databag:s,test/database.password,dbpass
[localhost] Executing task 'databag'
set key:test/database.password, value:dbpass

$ fab databag:g,test/database.password
[localhost] Executing task 'databag'
dbpass

$ fab databag:l,test
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
