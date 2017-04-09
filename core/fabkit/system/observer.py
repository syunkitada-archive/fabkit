# coding: utf-8

import re
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

        filer.mkdir(CONF._remote_stats_dir)
        dstat_csv = CONF._remote_stats_dir + '/dstat.csv'
        dstat_out = CONF._remote_stats_dir + '/dstat.out'
        sudo("rm -rf {0}".format(dstat_csv))
        sudo("sh -c 'dstat -tTlpyirdfmsgn --output {0} > {1} &'".format(dstat_csv, dstat_out), pty=False)

    def stop(self):
        sudo("pkill dstat")
        self.update_stats()

    def update_stats(self):
        local_dstat_csv = os.path.join(self.stats_dir, '{0}_dstat.csv'.format(env.host))
        dstat_csv = CONF._remote_stats_dir + '/dstat.csv'

        local_wrk_csv = os.path.join(self.stats_dir, '{0}_wrk.csv'.format(env.host))
        wrk_out = CONF._remote_stats_dir + '/wrk.out'

        if filer.exists(dstat_csv):
            result = run('tail -n +6 {0}'.format(dstat_csv))
            with open(local_dstat_csv, 'w') as f:
                f.write(str(result))

        if filer.exists(wrk_out):
            result = run('cat {0}'.format(wrk_out))
            lines = str(result).split('\n')
            options = lines[1].strip().split(' ')
            threads = options[0]
            connections = options[3]

            t_latency = re.sub(r' +', ' ', lines[3].strip()).split(' ')[1:]
            t_rps = re.sub(r' +', ' ', lines[4].strip()).split(' ')[1:]
            rps = re.sub(r' +', ' ', lines[6].strip()).split(' ')[1]
            tps = re.sub(r' +', ' ', lines[7].strip()).split(' ')[1]
            csv = 'threads,connections,rps,tps,t_latency_avg,t_latency_stdev,t_latency_max,t_latency_stdev,t_rps_avg,t_rps_stdev,t_rps_max,t_rps_stdev\n'
            csv += '{t},{c},{rps},{tps},{t_latency},{t_rps}'.format(
                t=threads, c=connections, rps=rps, tps=tps, t_latency=','.join(t_latency), t_rps=','.join(t_rps)
            )
            with open(local_wrk_csv, 'w') as f:
                f.write(csv)

    def wrk(self, c, t, d, url):
        wrk_out = CONF._remote_stats_dir + '/wrk.out'
        sudo('wrk -c {c} -t {t} -d {d} {url} > {out} &'.format(
            c=c, t=t, d=d, url=url, out=wrk_out), pty=False)
