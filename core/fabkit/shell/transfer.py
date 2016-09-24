# coding: utf-8

from fabkit import api
from base import run, sudo, expect, local
from oslo_config import cfg

CONF = cfg.CONF


def scp(from_path, to_path, is_local=True, is_receive=False, use_env_host=True):
    if is_receive:
        target = CONF._remote_tmp_dir + from_path
        target_dir = target.rsplit('/', 1)[0]
        run('mkdir -p {0}'.format(target_dir))
        cmd = 'scp -P {0} -o "StrictHostKeyChecking=no" -o "UserKnownHostsFile=/dev/null" {1}@{2}:{3} {4}'.format(
            api.env.port, api.env.user, api.env.host, target, to_path)

        if CONF.user and CONF.password:
            result = expect(
                cmd,
                [['* password:', '{0}\\n'.format(CONF.password)]],
                is_local=is_local)

        else:
            result = local(cmd)

        return result

    else:
        cmd = 'scp -P {0} -o "StrictHostKeyChecking=no" -o "UserKnownHostsFile=/dev/null" {1} {2}@'.format(
            api.env.port, from_path, api.env.user)
        if use_env_host:
            cmd += '{0}:'.format(api.env.host)

        if is_local:
            tmp_target = CONF._remote_tmp_dir + to_path
            tmp_target_dir = tmp_target.rsplit('/', 1)[0]

            run('mkdir -p {0}'.format(tmp_target_dir))
            cmd += tmp_target

            if CONF.user and CONF.password:
                result = expect(
                    cmd,
                    [['* password:', '{0}\\n'.format(CONF.password)]],
                    is_local=is_local)

            else:
                result = local(cmd)

            sudo('cp {0} {1}'.format(tmp_target, to_path))
            return result

        else:
            cmd += to_path
            return run(cmd)
