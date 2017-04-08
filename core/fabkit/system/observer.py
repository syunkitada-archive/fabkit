# coding: utf-8

from fabkit import api, log, run, sudo, env, filer
import os
from oslo_config import cfg

CONF = cfg.CONF


class Observer():
    def __init__(self):
        print 'DEBUG'
        self.targets = ['cpu']
        env.cluster
        self.stats_dir = os.path.join(CONF._node_dir, env.cluster['name'], 'stats')
        if not os.path.exists(self.stats_dir):
            os.mkdir(self.stats_dir)

    def start(self, targets=None):
        if targets is not None:
            self.targets = targets

        self.local_dstat_csv = os.path.join(self.stats_dir, '{0}_dstats.csv'.format(env.host))
        filer.mkdir(CONF._remote_stats_dir)
        dstat_csv = CONF._remote_stats_dir + '/dstat.csv'
        dstat_out = CONF._remote_stats_dir + '/dstat.out'
        sudo("rm -rf {0}".format(dstat_csv))
        sudo("sh -c 'dstat -tTlpyirdfmsgn --output {0} > {1} &'".format(dstat_csv, dstat_out), pty=False)

    def stop(self):
        sudo("pkill dstat")
        self.update_stats()

    def update_stats(self):
        dstat_csv = CONF._remote_stats_dir + '/dstat.csv'
        result = run('tail -n +6 {0}'.format(dstat_csv))
        with open(self.local_dstat_csv, 'w') as f:
            f.write(str(result))
