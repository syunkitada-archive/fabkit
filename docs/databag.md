# Task databag


access databag

## Args
* option (str): action option
  * set: set databag
  * get: get databag
  * list: show databag list

## Examples
``` bash
$ fab databag:set,test/database.password,dbpass
[localhost] Executing task 'databag'
set key:test/database.password, value:dbpass

$ fab databag:get,test/database.password
[localhost] Executing task 'databag'
dbpass

$ fab databag:list
...
```
