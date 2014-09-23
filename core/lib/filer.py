# coding: utf-8

import time
from lib.api import local, sudo, local_scp
from lib import log


def template(target, src_file, owner='root:root', mode='644', kwargs={}):
    timestamp = int(time.time())
    tmp_file = '/tmp/chefric{0}_{1}'.format(src_file, timestamp)
    tmp_dir = tmp_file.rsplit('/', 1)[0]
    mkdir(tmp_dir, is_local=True)
    mkdir(tmp_dir)

    with open(src_file, 'rb') as f:
        with open(tmp_file, 'w') as exf:
            exf.write(f.read().format(**kwargs))

    local_scp(tmp_file, tmp_file)
    result = sudo('diff {0} {1}'.format(target, tmp_file))
    if result.return_code != 0:
        sudo('mv {0} {1}_old'.format(target, tmp_file))
        sudo('cp -af {0} {1}'.format(tmp_file, target))
    else:
        log.info('No change')

    sudo('chmod {0} {1}'.format(mode, target))
    sudo('chown {0} {1}'.format(owner, target))


def mkdir(name, is_local=False):
    cmd_mkdir = 'mkdir -p {0}'.format(name)
    if is_local:
        local(cmd_mkdir)
    else:
        sudo(cmd_mkdir)
