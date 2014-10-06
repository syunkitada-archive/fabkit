# coding: utf-8

import time
import os
from fabric.api import env, warn_only
from lib.api import local, sudo, scp
from lib import (log,
                 conf)


def template(target, src_file, owner='root:root', mode='644', kwargs={}):
    # TODO 新規ファイルの場合は、全diffを表示する
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
            exf.write(f.read().format(**kwargs))

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
