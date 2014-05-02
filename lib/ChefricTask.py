# coding: utf-8

from fabric.tasks import Task
import commands
import conf, util

class ChefricTask(Task):
    def __init__(self, func, *args, **kwargs):
        super(ChefricTask, self).__init__(*args, **kwargs)
        self.func = func

    def run(self, *args, **kwargs):
        return self.func(*args, **kwargs)


