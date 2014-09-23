# coding: utf-8

from fabric import api
from lib import util
from fabric.tasks import Task


class LogTask(Task):
    def __init__(self, func, *args, **kwargs):
        super(LogTask, self).__init__(*args, **kwargs)
        self.func = func

    def run(self, *args, **kwargs):
        result = self.func(*args, **kwargs)
        print api.env.tasks
        print api.env.command
        command = api.env.command

        host_json = util.load_json()
        api.env.last_runs.append('{0} [{1}:{2}]'.format(util.get_timestamp(), command, result))

        host_json.update({'last_runs': api.env.last_runs})

        util.dump_json(host_json)
        return result
