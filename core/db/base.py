# coding: utf-8

import os
from oslo_config import cfg
from oslo_db.sqlalchemy import session as db_session

CONF = cfg.CONF


class Connection():

    def __init__(self):
        options = dict(CONF.database.items())
        url = options['connection']
        self.engine_facade = db_session.EngineFacade(url, **options)

    def db_sync(self):
        # NOTE: to minimise memory, only import migration when needed
        from oslo_db.sqlalchemy import migration
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                            'sqlalchemy', 'migrate_repo')
        migration.db_sync(self.engine_facade.get_engine(), path)
