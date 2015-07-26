# coding: utf-8

import time
import os
import inspect
from fabkit import api, env, local, sudo, scp, conf, log
from jinja2 import Template


def create_src_file(target, src_str):
    if target[0] == '/':
        target = target[1:]

    local_tmp_file = os.path.join(conf.TMP_DIR, env.host, 'src_files', target)

    if not os.path.exists(local_tmp_file):
        os.makedirs(os.path.dirname(local_tmp_file))

    with open(local_tmp_file, 'w') as f:
        f.write(src_str)

    return local_tmp_file


def __get_src_file(target, src_dirname, src_target=None, src_file=None):
    if not src_file:
        stack = inspect.stack()[1:-11]
        srcs_dirs = []
        for frame in stack:
            file = frame[1]
            if file.find(conf.FABLIB_MODULE_DIR) == 0 or file.find(conf.FABSCRIPT_MODULE_DIR) == 0:
                srcs_dir = os.path.join(os.path.dirname(frame[1]), src_dirname)
                if os.path.exists(srcs_dir):
                    srcs_dirs.insert(0, srcs_dir)

        if not src_target:
            src_target = target.rsplit('/', 1)[1]

        for src in srcs_dirs:
            for root, dirs, files in os.walk(src):
                for file in files:
                    if file == src_target:
                        src_file = os.path.join(root, src_target)
                        return src_file
    else:
        return src_file


def file(target, mode='644', owner='root:root', src_file=None, src_str=None):
    if src_str:
        src_file = create_src_file(target, src_str)

    is_updated = False
    with api.warn_only():
        if exists(target):
            log.info('file "{0}" exists'.format(target))
        else:
            tmp_target = target

            if not src_file:
                src_file = __get_src_file(tmp_target, src_dirname='files')

            scp(src_file, target)
            sudo('cp -arf {0} {1}'.format(src_file, target))
            is_updated = True

    sudo('chmod -R {0} {1}'.format(mode, target)
         + ' && chown -R {0} {1}'.format(owner, target))
    return is_updated


def template(target, mode='644', owner='root:root', data={},
             src_target=None, src_file=None, src_str=None):
    is_updated = False

    if src_str:
        src_file = create_src_file(target, src_str)

    if not src_file:
        src_file = __get_src_file(target, src_dirname='templates', src_target=src_target)

    timestamp = int(time.time())
    tmp_path = 'templates/{0}_{1}'.format(target, timestamp)
    tmp_path = os.path.join(conf.REMOTE_STORAGE_DIR, tmp_path)
    # local_tmp_file = os.path.join(conf.TMP_DIR, env.host, tmp_path)
    local_tmp_file = conf.TMP_DIR + '/' + env.host + '/' + tmp_path

    local_tmp_dir = local_tmp_file.rsplit('/', 1)[0]
    mkdir(local_tmp_dir, is_local=True)

    tmp_dir = tmp_path.rsplit('/', 1)[0]
    mkdir(tmp_dir, mode='770', owner='{0}:root'.format(env.user))

    with open(src_file, 'rb') as f:
        template = Template(f.read().decode('utf-8'))
        with open(local_tmp_file, 'w') as exf:
            exf.write(template.render(**data).encode('utf-8'))

    scp(local_tmp_file, tmp_path)

    with api.warn_only():
        if exists(target):
            result = sudo('diff {0} {1}'.format(target, tmp_path))
            if result.return_code != 0:
                sudo('mv {0} {1}_old'.format(target, tmp_path))
                sudo('cp -af {0} {1}'.format(tmp_path, target))
                is_updated = True
            else:
                log.info('No change')
        else:
            sudo('diff /dev/null {1}'.format(target, tmp_path))
            sudo('cp -af {0} {1}'.format(tmp_path, target))
            is_updated = True

    sudo('sh -c "chmod {0} {1}'.format(mode, target)
         + ' && chown {0} {1}"'.format(owner, target))

    return is_updated


def mkdir(target, is_local=False, owner='root:root', mode='775'):
    cmd_mkdir = 't={0} && mkdir -p $t'.format(target)
    if is_local:
        local(cmd_mkdir)
    else:
        sudo('{0} && chmod {1} $t && chown {2} $t'.format(cmd_mkdir, mode, owner))


def touch(target, is_local=False, owner='root:root', mode='775'):
    cmd_touch = 't={0} && touch $t'.format(target)
    if is_local:
        local(cmd_touch)
    else:
        sudo('{0} && chmod {1} $t && chown {2} $t'.format(cmd_touch, mode, owner))


def exists(target):
    with api.warn_only():
        cmd = '[ -e {0} ]'.format(target)
        return True if sudo(cmd).return_code == 0 else False
