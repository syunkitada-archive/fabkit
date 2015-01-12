#!/bin/sh -x

pushd fabfile/core/webapp
./manage.py runserver `hostname`:8888
popd
