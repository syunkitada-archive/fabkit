# coding: utf-8

import re
import os
import commands
import yaml
from apps.fabscript.models import Fabscript
from django.db import transaction
from fabkit import env, conf


def load_fabscript(fabscript_name):
    if fabscript_name not in env.fabscript_map:
        RE_FABSCRIPT_YAML = re.compile('(.*\.yaml)'.format(conf.FABSCRIPT_MODULE_DIR))
        fabscript_dir = os.path.join(conf.FABSCRIPT_MODULE_DIR,
                                     fabscript_name.rsplit('.', 1)[0].replace('.', '/'))
        cmd = 'find {0} -maxdepth 1 -name "__*.yaml"'.format(fabscript_dir)
        finded_fabscript = commands.getoutput(cmd)

        fabscript_yamls = set(RE_FABSCRIPT_YAML.findall(finded_fabscript))
        fabscript = {}
        for fabscript_yaml in fabscript_yamls:
            with open(fabscript_yaml, 'r') as f:
                fabscript.update(yaml.load(f.read()))

        env.fabscript_map[fabscript_name] = fabscript


def get_fabscript(script_name):
    try:
        fabscript = Fabscript.objects.get(name=script_name)
        if fabscript.is_deleted:
            fabscript.is_deleted = False
            fabscript.save()
    except Fabscript.DoesNotExist:
        create_fabscript(script_name)

    return fabscript


@transaction.atomic
def create_fabscript(script_name):
    fabscript = Fabscript(name=script_name)
    fabscript.save()
