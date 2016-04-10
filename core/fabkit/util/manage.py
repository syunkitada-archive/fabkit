# coding: utf-8

import os
import re
import commands
from fabkit import env
from fabkit.conf import conf_base
from oslo_config import cfg
import pickle

CONF = cfg.CONF
all_fablib_map = {}
requresive_fablib_map = {}
re_giturl = re.compile('.*\.git')
re_lndir = re.compile('ln:.*')


# create directory, if directory not exists
def create_dir(directory, is_create_init_py=False):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print '"{0}" is created.'.format(directory)
        if is_create_init_py:
            init_py = os.path.join(directory, '__init__.py')
            with open(init_py, 'w') as f:
                f.write('# coding: utf-8')
                print '"{0} is created."'.format(init_py)


def git_clone_required_fablib(is_test=False):
    if is_test:
        for fablib_name, src in CONF.test.fablib.items():
            if re_giturl.match(src):
                git_clone(fablib_name, src)
            elif re_lndir.match(src):
                create_link(fablib_name, src)

    for fablib_name, src in CONF.fablib.items():
        if re_giturl.match(src):
            git_clone(fablib_name, src)
        elif re_lndir.match(src):
            create_link(fablib_name, src)

    for fablib_name, src in requresive_fablib_map.items():
        if re_giturl.match(src):
            git_clone_requresive(fablib_name, src)

    for fablib_name, git_repo in all_fablib_map.items():
        git_pull(fablib_name, git_repo)


def git_clone(fablib_name, git_repo):
    fablib = os.path.join(CONF._fablib_module_dir, fablib_name)
    fabfile_ini = os.path.join(fablib, 'test-repo', 'fabfile.ini')

    if not os.path.exists(fablib):
        cmd_gitclone = 'git clone {0} {1}'.format(git_repo, fablib)
        print cmd_gitclone
        (status, output) = commands.getstatusoutput(cmd_gitclone)
        print output
        if status != 0:
            exit(0)

    if os.path.exists(fabfile_ini):
        EX_CONF = cfg.ConfigOpts()
        EX_CONF([], default_config_files=[fabfile_ini])
        EX_CONF.register_opts(conf_base.default_opts)
        for fablib_name, git_repo in EX_CONF.fablib.items():
            all_fablib_map[fablib_name] = git_repo
            requresive_fablib_map[fablib_name] = git_repo


def create_link(fablib_name, src):
    fablib = os.path.join(CONF._fablib_module_dir, fablib_name)
    src = src[3:]
    if not os.path.exists(fablib):
        print 'create link {0}'.format(fablib)
        os.symlink(src, fablib)


def git_clone_requresive(fablib_name, git_repo):
    fablib = os.path.join(CONF._fablib_module_dir, fablib_name)
    if not os.path.exists(fablib):
        cmd_gitclone = 'git clone {0} {1}'.format(git_repo, fablib)
        print cmd_gitclone
        (status, output) = commands.getstatusoutput(cmd_gitclone)
        print output
        if status != 0:
            exit(0)

    fabfile_ini = os.path.join(fablib, 'test-repo', 'fabfile.ini')
    if os.path.exists(fabfile_ini):
        EX_CONF = cfg.ConfigOpts()
        EX_CONF([], default_config_files=[fabfile_ini])
        EX_CONF.register_opts(conf_base.default_opts)
        for fablib_name, git_repo in EX_CONF.fablib.items():
            all_fablib_map[fablib_name] = git_repo
            git_clone_requresive(fablib_name, git_repo)


def git_pull(fablib_name, git_repo):
    fablib = os.path.join(CONF._fablib_module_dir, fablib_name)
    if os.path.exists(fablib):
        cmd_gitclone = 'cd {0} && git pull'.format(fablib)
        print cmd_gitclone
        (status, output) = commands.getstatusoutput(cmd_gitclone)
        print output
        if status != 0:
            exit(0)


def create_required_dirs():
    create_dir(CONF._storage_dir)
    create_dir(CONF._databag_dir)
    create_dir(CONF._tmp_dir)
    create_dir(CONF._node_dir)
    create_dir(CONF._handler_dir, True)
    create_dir(CONF._fabscript_module_dir, True)
    create_dir(CONF._fablib_module_dir, True)

    if not os.path.exists(CONF._node_meta_pickle):
        node_meta = {
            'recent_clusters': [],
        }

        with open(CONF._node_meta_pickle, 'w') as f:
            pickle.dump(node_meta, f)
