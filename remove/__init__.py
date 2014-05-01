from fabric.api import *
import re, os, json, commands, sys
from types import *
import datetime
import util, conf
import os

@task
def remove():
    is_remove = raw_input('\n you want to remove above hosts. (y/n)') == 'y'
    print is_remove
    return
    for hostname in env.hosts:
        util.remove_json(hostname)

    return


