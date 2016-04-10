from __future__ import with_statement
from alembic import context
# from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig

# for oslo
from oslo_config import cfg
from oslo_db.sqlalchemy import session

import os
import sys
ALEMBIC_DIR = os.path.dirname(os.path.abspath(__file__))
CORE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(ALEMBIC_DIR)))
REPO_DIR = os.path.dirname(os.path.dirname(CORE_DIR))
sys.path.extend([CORE_DIR])
from fabkit.conf import conf_base
conf_base.init(REPO_DIR)

CONF = cfg.CONF

db_dir = os.path.join(os.path.dirname(__file__), '../')
sys.path.extend([db_dir])

from db.impl_sqlalchemy.models import Base
target_metadata = Base.metadata


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # url = config.get_main_option("sqlalchemy.url")
    url = CONF.database.connection
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    url = CONF.database.connection
    engine = session.create_engine(url)
    connection = engine.connect()

    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )

    with context.begin_transaction():
        context.run_migrations()

    # connectable = engine_from_config(
    #     config.get_section(config.config_ini_section),
    #     prefix='sqlalchemy.',
    #     poolclass=pool.NullPool)

    # with connectable.connect() as connection:
    #     context.configure(
    #         connection=connection,
    #         target_metadata=target_metadata
    #     )

    #     with context.begin_transaction():
    #         context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
