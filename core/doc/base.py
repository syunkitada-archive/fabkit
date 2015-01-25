# coding: utf-8

from databag import databag
from sync import sync
from node import node
from fabkit import api, conf
from jinja2 import Template
import os


@api.task
def doc(option):
    if option == 'dump':
        dump_doc(node)
        dump_doc(databag)
        dump_doc(sync)

    elif option == 'node':
        print_doc(node)
    elif option == 'databag':
        print_doc(databag)
    elif option == 'sync':
        print_doc(sync)


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
