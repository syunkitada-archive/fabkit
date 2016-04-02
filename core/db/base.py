# coding: utf-8

from oslo_config import cfg
from oslo_db.sqlalchemy import session as db_session

CONF = cfg.CONF


class Connection():

    def __init__(self):
        options = dict(CONF.database.items())
        url = options['connection']
        self.engine_facade = db_session.EngineFacade(url, **options)
