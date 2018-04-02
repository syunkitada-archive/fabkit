# Sqlalchemy

## init alembic_migrations
``` bash
$ pwd
./fabkit-repo/fabfile/core/pdns/impl_sqlalchemy/

$ alembic init alembic_migrations
...

$ cd alembic_migrations
$ pwd
./fabkit-repo/fabfile/core/db/impl_sqlalchemy/alembic_migrations

# edit env.py for oslo_config
$ vim env.py
5a6,27
> # for oslo
> from oslo_config import cfg
> from oslo_db.sqlalchemy import session
>
> import os
> import sys
> ALEMBIC_DIR = os.path.dirname(os.path.abspath(__file__))
> CORE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(ALEMBIC_DIR)))
> REPO_DIR = os.path.dirname(os.path.dirname(CORE_DIR))
> sys.path.extend([CORE_DIR])
> from fabkit.conf import conf_base
> conf_base.init(REPO_DIR)
>
> CONF = cfg.CONF
>
> db_dir = os.path.join(os.path.dirname(__file__), '../')
> sys.path.extend([db_dir])
>
> from db.impl_sqlalchemy.models import Base
> target_metadata = Base.metadata
>
>
18c40
< target_metadata = None
---
> # target_metadata = None
38c60,61
<     url = config.get_main_option("sqlalchemy.url")
---
>     # url = config.get_main_option("sqlalchemy.url")
>     url = CONF.database.connection
53,62c76,97
<     connectable = engine_from_config(
<         config.get_section(config.config_ini_section),
<         prefix='sqlalchemy.',
<         poolclass=pool.NullPool)
<
<     with connectable.connect() as connection:
<         context.configure(
<             connection=connection,
<             target_metadata=target_metadata
<         )
---
>     url = CONF.database.connection
>     engine = session.create_engine(url)
>     connection = engine.connect()
>
>     context.configure(
>         connection=connection,
>         target_metadata=target_metadata
>     )
>
>     with context.begin_transaction():
>         context.run_migrations()
>
>     # connectable = engine_from_config(
>     #     config.get_section(config.config_ini_section),
>     #     prefix='sqlalchemy.',
>     #     poolclass=pool.NullPool)
>
>     # with connectable.connect() as connection:
>     #     context.configure(
>     #         connection=connection,
>     #         target_metadata=target_metadata
>     #     )
64,65c99,100
<         with context.begin_transaction():
<             context.run_migrations()
---
>     #     with context.begin_transaction():
>     #         context.run_migrations()


# create init versions
$ /opt/fabkit/bin/alembic revision --autogenerate -m "init"
INFO  [alembic.runtime.migration] Context impl MySQLImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'agent'
  Generating /home/owner/fabkit-repo/fabfile/core/db/sqlalchemy/alembic_migrations/versions/ef338fa9777a_init.py ... done
```


## create versions
```
$ pwd
./fabkit-repo/fabfile/core/db/sqlalchemy/alembic_migrations

$ alembic revision --autogenerate -m "[message]"
```
* (Reference of the messag)[https://github.com/openstack/neutron/tree/stable/liberty/neutron/db/migration/alembic_migrations/versions]


## sync db
```
$ pwd
./fabkit-repo/fabfile/core/db/sqlalchemy/alembic_migrations

# sync db to head
$ alembic upgrade head
```

## fab command
``` bash
# update model
$ fab sync_db:generate,m=hoge

# sync db
$ fab sync_db
```
