# coding: utf-8

import os
import yaml
from oslo_config import cfg

CONF = cfg.CONF


def update_fabscript_map(fabscript_map):
    for fabscript_name, fabscript in fabscript_map.items():
        splited_name = fabscript_name.rsplit('/', 1)
        fabscript_cluster = splited_name[0]
        script = splited_name[1]
        fabscript_yaml = os.path.join(
            CONF._fabscript_module_dir, fabscript_cluster, '__fabscript.yml')
        if os.path.exists(fabscript_yaml):
            with open(fabscript_yaml, 'r') as f:
                data = yaml.load(f)
                if data is not None:
                    fabscript.update(data.get(script, {}))
