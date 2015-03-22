# noqa

from fabkit import api, env, conf, local, os, scp, run, util, parallel
import yaml


@parallel
def run_remote():
    remote = env.remote_map[env.host]

    root, dirname = conf.REPO_DIR.rsplit('/', 1)
    storage_dir = os.path.join(dirname, conf.STORAGE_DIR.rsplit('/', 1)[1])

    repo_tar = '{0}/fabrepo.tar.gz'.format(conf.TMP_DIR)
    remote_repo = '{0}/fabrepo'.format(conf.REMOTE_TMP_DIR)
    remote_repo_tar = '{0}/fabrepo.tar.gz'.format(conf.REMOTE_TMP_DIR)
    local('cd {0} && tar -zcf {1} {2} --exclude .git --exclude {3}'.format(
        root, repo_tar, dirname, storage_dir))
    scp(repo_tar, remote_repo_tar)
    run('rm -rf $HOME/fabric-repo')
    run('cd {0} && tar -xf fabrepo.tar.gz -C $HOME'.format(conf.REMOTE_TMP_DIR, remote_repo))

    task_name = ''
    if env.is_setup:
        task_name = 'setup'
    elif env.is_check:
        task_name = 'check'
    elif env.is_manage:
        task_name = 'manage:{0}'.format(','.join(env.func_names))

    cluster_map = {}
    with api.shell_env(password=env.password):
        for cluster in remote['clusters']:
            run('cd $HOME/{0} && fab node:{1}/{2},yes {3} -u $USER -p $password'.format(
                dirname, cluster, remote['host_pattern'], task_name, env.password))
            with api.warn_only():
                yaml_str = run('cat $HOME/{0}/nodes/{1}/__cluster.yml'.format(dirname, cluster))
            cluster_map[cluster] = yaml.load(yaml_str)

    return cluster_map
