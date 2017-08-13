# coding: utf-8

import time
import os
import inspect
from fabkit import api, env, run, sudo, scp, log, cmd
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from oslo_config import cfg


CONF = cfg.CONF
j2_env = Environment(
    loader=FileSystemLoader('/', encoding='utf-8'),
    undefined=StrictUndefined)


def create_src_file(dest, src_str):
    if dest[0] == '/':
        dest = dest[1:]

    local_tmp_file = os.path.join(CONF._tmp_dir, env.host, 'src_files', dest)

    dir_path = os.path.dirname(local_tmp_file)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    with open(local_tmp_file, 'w') as f:
        f.write(src_str)

    return local_tmp_file


def __get_src_file(dest, src_dirname, src=None, src_file=None):
    if not src_file:
        stack = inspect.stack()
        srcs_dirs = []
        for frame in stack:
            file = frame[1]
            if file.find(CONF._fablib_module_dir) == 0 \
                    or file.find(CONF._fabscript_module_dir) == 0:
                srcs_dir = os.path.join(os.path.dirname(frame[1]), src_dirname)
                if os.path.exists(srcs_dir):
                    srcs_dirs.insert(0, srcs_dir)

        if not src:
            src = dest.rsplit('/', 1)[1]

        for srcs_dir in srcs_dirs:
            for root, dirs, files in os.walk(srcs_dir):
                src_file = os.path.join(root, src)
                if os.path.exists(src_file):
                    return src_file
                else:
                    src_file = src_file + '.j2'
                    if os.path.exists(src_file):
                        return src_file

        raise('src_file does not found.')
    else:
        return src_file


def file(dest, mode='644', owner='root:root', src=None, src_file=None, src_str=None,
         override=False):
    if src_str is not None:
        src_file = create_src_file(dest, src_str)

    is_updated = False
    with api.warn_only():
        if exists(dest) and not override:
            log.info('file "{0}" exists'.format(dest))
        else:
            if not src_file:
                src_file = __get_src_file(dest, src_dirname='files', src=src)

            if env.is_local:
                sudo('cp {0} {1}'.format(src_file, dest))
            else:
                scp(src_file, dest)
            is_updated = True

    sudo('chmod -R {0} {1}'.format(mode, dest)
         + ' && chown -R {0} {1}'.format(owner, dest))
    return is_updated


def template(dest, mode='644', owner='root:root', data={},
             src=None, src_file=None, src_str=None, insert_eol_crlf=True):
    template_data = {}
    template_data.update(data)
    template_data['node'] = env.node
    template_data['cluster'] = env.cluster
    is_updated = False

    if src_str:
        src_file = create_src_file(dest, src_str)

    if not src_file:
        src_file = __get_src_file(dest, src_dirname='templates', src=src)

    timestamp = int(time.time())
    tmp_path = 'templates/{0}_{1}'.format(dest, timestamp)
    tmp_path = os.path.join(CONF._remote_storage_dir, tmp_path)
    # local_tmp_file = os.path.join(conf.TMP_DIR, env.host, tmp_path)
    local_tmp_file = CONF._tmp_dir + '/' + env.host + '/' + tmp_path

    local_tmp_dir = local_tmp_file.rsplit('/', 1)[0]
    mkdir(local_tmp_dir, is_local=True, use_sudo=False)

    template = j2_env.get_template(src_file)
    if not env.is_test:
        with open(local_tmp_file, 'w') as exf:
            exf.write(template.render(**template_data).encode('utf-8'))
            if insert_eol_crlf:
                exf.write('\n')

    if env.is_local:
        with api.warn_only():
            if exists(dest):
                result = sudo('diff {0} {1}'.format(dest, local_tmp_file))
                if result.return_code != 0:
                    sudo('mv {0} {1}_old'.format(dest, local_tmp_file))
                    sudo('cp -f {0} {1}'.format(local_tmp_file, dest))
                    is_updated = True
                else:
                    log.info('No change')
            else:
                sudo('diff /dev/null {1}'.format(dest, local_tmp_file))
                sudo('cp -f {0} {1}'.format(local_tmp_file, dest))
                is_updated = True
    else:
        tmp_dir = tmp_path.rsplit('/', 1)[0]
        mkdir(tmp_dir, mode='770', owner='{0}:root'.format(env.user))
        scp(local_tmp_file, tmp_path)

        with api.warn_only():
            if exists(dest):
                result = sudo('diff {0} {1}'.format(dest, tmp_path))
                if result.return_code != 0:
                    sudo('mv {0} {1}_old'.format(dest, tmp_path))
                    sudo('cp -f {0} {1}'.format(tmp_path, dest))
                    is_updated = True
                else:
                    log.info('No change')
            else:
                sudo('diff /dev/null {1}'.format(dest, tmp_path))
                sudo('cp -f {0} {1}'.format(tmp_path, dest))
                is_updated = True

    sudo('sh -c "chmod {0} {1}'.format(mode, dest)
         + ' && chown {0} {1}"'.format(owner, dest))

    return is_updated


def mkdir(dest, is_local=False, owner='root:root', mode='775', use_sudo=True):
    cmd_mkdir = 't={0} && mkdir -p $t'.format(dest)
    if is_local or env.is_local:
        if use_sudo:
            sudo("sh -c '{0} && chmod {1} $t && chown {2} $t'".format(cmd_mkdir, mode, owner))
        else:
            cmd(cmd_mkdir)

    elif use_sudo:
        sudo('{0} && chmod {1} $t && chown {2} $t'.format(cmd_mkdir, mode, owner))
    else:
        run('{0} $t'.format(cmd_mkdir, mode, owner))


def touch(dest, is_local=False, owner='root:root', mode='775'):
    cmd_touch = 't={0} && touch $t'.format(dest)
    if is_local or env.is_local:
        cmd(cmd_touch)
    else:
        sudo('{0} && chmod {1} $t && chown {2} $t'.format(cmd_touch, mode, owner))


def exists(dest, is_local=False):
    cmd_exists = '[ -e {0} ]'.format(dest)
    if is_local or env.is_local:
        result, result_out = cmd(cmd_exists)
        return True if result == 0 else False
    else:
        with api.warn_only():
            return True if sudo(cmd_exists).return_code == 0 else False
