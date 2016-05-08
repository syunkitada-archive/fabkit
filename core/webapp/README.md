# Webapp

## Initial setup
``` bash
# create database
./manage.py migrate

# start test server
./manage.py runserver `hostname`:8080
```

``` bash
# Install Node.js

# install npm packages
$ npm install -g grunt-cli
$ npm install

# start grunt
$ grunt
```


## Create migrations files
If you change models of apps, make migrations file of apps.
``` bash
$ manage.py makemigrations chat

$ ls -l web_apps/chat/migrations
-rw-rw-r-- 1 owner owner 2.0K  5月  5 16:48 0001_initial.py
-rw-rw-r-- 1 owner owner    0  5月  5 16:48 __init__.py
-rw-rw-r-- 1 owner owner  167  5月  5 16:48 __init__.pyc
```
