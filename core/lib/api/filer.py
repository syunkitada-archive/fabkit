# coding: utf-8

import time
import os
import inspect
from fabric.api import env, warn_only
from api import local, sudo, scp, run
from lib import log, conf
from jinja2 import Template


def __get_src_file(target, file_type, src_file=None):
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

        file_name = target.rsplit('/', 1)[1]
        for src in srcs_dirs:
            src_file = os.path.join(src, file_name)
            if os.path.exists(src_file):
                return src_file
    else:
        return src_file


def file(target, mode='644', owner='root:root', extension=None, src_file=None):
    with warn_only():
        if exists(target):
            log.info('file "{0}" exists'.format(target))
        else:
            if extension:
                tmp_target = '{0}.{1}'.format(target, extension)
            else:
                tmp_target = target

            src_file = __get_src_file(tmp_target, file_type='file')

            tmp_file = '/tmp/file/{0}'.format(tmp_target)
            tmp_dir = tmp_file.rsplit('/', 1)[0]
            print 'DEBUG\n\n'
            print tmp_target
            print tmp_file
            print tmp_dir
            mkdir(tmp_dir, mode='777')

            scp(src_file, tmp_file)

            if extension:
                if extension == 'tar.gz':
                    run('tar -xvf {0} -C {1}'.format(tmp_file, tmp_dir))
                sudo('cp -arf /tmp/file/{0} {0}'.format(target))
            else:
                sudo('cp -arf {0} {1}'.format(tmp_file, target))

    sudo('chmod -R {0} {1}'.format(mode, target))
    sudo('chown -R {0} {1}'.format(owner, target))


def template(target, mode='644', owner='root:root', data={}, src_file=None):
    src_file = __get_src_file(target, file_type='template')
    timestamp = int(time.time())
    tmp_path = 'template/{0}_{1}'.format(target, timestamp)
    local_tmp_file = os.path.join(conf.TMP_DIR, env.host, tmp_path)
    tmp_file = os.path.join('/tmp', tmp_path)

    local_tmp_dir = local_tmp_file.rsplit('/', 1)[0]
    mkdir(local_tmp_dir, is_local=True)

    tmp_dir = tmp_file.rsplit('/', 1)[0]
    mkdir(tmp_dir, mode='777')

    with open(src_file, 'rb') as f:
        with open(local_tmp_file, 'w') as exf:
            template = Template(f.read())
            exf.write(template.render(**data))

    scp(local_tmp_file, tmp_file)

    with warn_only():
        if exists(target):
            result = sudo('diff {0} {1}'.format(target, tmp_file))
            if result.return_code != 0:
                sudo('mv {0} {1}_old'.format(target, tmp_file))
                sudo('cp -af {0} {1}'.format(tmp_file, target))
            else:
                log.info('No change')
        else:
            sudo('diff /dev/null {1}'.format(target, tmp_file))
            sudo('cp -af {0} {1}'.format(tmp_file, target))

    sudo('chmod {0} {1}'.format(mode, target))
    sudo('chown {0} {1}'.format(owner, target))


def mkdir(target, is_local=False, owner='root:root', mode='775'):
    cmd_mkdir = 'mkdir -p {0}'.format(target)
    if is_local:
        local(cmd_mkdir)
    else:
        sudo(cmd_mkdir)
        sudo('chmod {0} {1}'.format(mode, target))
        sudo('chown {0} {1}'.format(owner, target))


def exists(target):
    with warn_only():
        cmd = '[ -e {0} ]'.format(target)
        if sudo(cmd).return_code == 0:
            return True
        else:
            return False
