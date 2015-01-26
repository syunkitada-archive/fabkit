# coding: utf-8

import time
import os
import inspect
from fabkit import api, env, local, sudo, run, scp, conf, log
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


def __get_src_file(target, file_type, src_target=None, src_file=None):
    if not src_file:
        stack = inspect.stack()[1:-11]
        srcs_dirs = []
        src_dirname = '{0}s'.format(file_type)
        for frame in stack:
            file = frame[1]
            if file.find(conf.FABLIB_MODULE_DIR) == 0 or file.find(conf.FABSCRIPT_MODULE_DIR) == 0:
                srcs_dir = os.path.join(os.path.dirname(frame[1]), src_dirname)
                if os.path.exists(srcs_dir):
                    srcs_dirs.insert(0, srcs_dir)

        print src_target
        if not src_target:
            src_target = target.rsplit('/', 1)[1]

        for src in srcs_dirs:
            src_file = os.path.join(src, src_target)
            if os.path.exists(src_file):
                return src_file
    else:
        return src_file


def file(target, mode='644', owner='root:root', extension=None, src_file=None, src_str=None):
    if src_str:
        src_file = create_src_file(target, src_str)

    is_updated = False
    with api.warn_only():
        if exists(target):
            log.info('file "{0}" exists'.format(target))
        else:
            if extension:
                tmp_target = '{0}.{1}'.format(target, extension)
            else:
                tmp_target = target

            if not src_file:
                src_file = __get_src_file(tmp_target, file_type='file')

            tmp_file = '/tmp/file/{0}'.format(tmp_target)
            tmp_dir = tmp_file.rsplit('/', 1)[0]
            mkdir(tmp_dir, mode='777')

            scp(src_file, tmp_file)

            if extension:
                if extension == 'tar.gz':
                    run('tar -xvf {0} -C {1}'.format(tmp_file, tmp_dir))
                sudo('cp -arf /tmp/file/{0} {0}'.format(target))
            else:
                sudo('cp -arf {0} {1}'.format(tmp_file, target))
            is_updated = True

    sudo('chmod -R {0} {1}'.format(mode, target))
    sudo('chown -R {0} {1}'.format(owner, target))
    return is_updated


def template(target, mode='644', owner='root:root', data={},
             src_target=None, src_file=None, src_str=None):
    is_updated = False

    if src_str:
        src_file = create_src_file(target, src_str)

    if not src_file:
        src_file = __get_src_file(target, file_type='template', src_target=src_target)

    timestamp = int(time.time())
    tmp_path = 'template/{0}_{1}'.format(target, timestamp)
    local_tmp_file = os.path.join(conf.TMP_DIR, env.host, tmp_path)
    tmp_file = os.path.join('/tmp', tmp_path)

    local_tmp_dir = local_tmp_file.rsplit('/', 1)[0]
    mkdir(local_tmp_dir, is_local=True)

    tmp_dir = tmp_file.rsplit('/', 1)[0]
    mkdir(tmp_dir, mode='777')

    with open(src_file, 'rb') as f:
        template = Template(f.read().decode('utf-8'))
        with open(local_tmp_file, 'w') as exf:
            exf.write(template.render(**data).encode('utf-8'))

    scp(local_tmp_file, tmp_file)

    with api.warn_only():
        if exists(target):
            result = sudo('diff {0} {1}'.format(target, tmp_file))
            if result.return_code != 0:
                sudo('mv {0} {1}_old'.format(target, tmp_file))
                sudo('cp -af {0} {1}'.format(tmp_file, target))
                is_updated = True
            else:
                log.info('No change')
        else:
            sudo('diff /dev/null {1}'.format(target, tmp_file))
            sudo('cp -af {0} {1}'.format(tmp_file, target))
            is_updated = True

    sudo('chmod {0} {1}'.format(mode, target))
    sudo('chown {0} {1}'.format(owner, target))

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
