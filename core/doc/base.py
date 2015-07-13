# coding: utf-8

from databag import databag
from testtools import test
from node import node
from setup import setup, check, manage
from runserver import runserver
from fabkit import api, conf
from jinja2 import Template
import os


@api.task
def doc(option):
    if option == 'dump':
        dump_doc(check)
        dump_doc(doc)
        dump_doc(databag)
        dump_doc(manage)
        dump_doc(node)
        dump_doc(setup)
        dump_doc(runserver)
        dump_doc(test)
    elif option == 'check':
        print_doc(check)
    elif option == 'databag':
        print_doc(databag)
    elif option == 'doc':
        print_doc(doc)
    elif option == 'manage':
        print_doc(manage)
    elif option == 'node':
        print_doc(node)
    elif option == 'setup':
        print_doc(setup)
    elif option == 'runserver':
        print_doc(runserver)
    elif option == 'test':
        print_doc(test)


def dump_doc(func):
    task_doc = os.path.join(os.path.dirname(__file__), 'task.md')
    data = {
        'name': func.__name__,
        'doc': func.__doc__,
    }

    with open(task_doc, 'rb') as f:
        template = Template(f.read().decode('utf-8'))
        doc_text = template.render(data).encode('utf-8')
        with open(os.path.join(conf.DOC_DIR, '{0}.md'.format(func.__name__)), 'w') as wf:
            wf.write(doc_text)


def print_doc(func):
    print func.__name__
    print func.__doc__
