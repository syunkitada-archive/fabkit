# Sqlalchemy

## create migrate_repo
``` bash
$ alembic revision --autogenerate -m "Create table"
$ alembic upgrade head

neutron みるとスクリプトの中でこの工程を行えるようにしてる

https://github.com/openstack/neutron/blob/655a1a214736e91e2f0e6186c9650946883bea41/neutron/db/migration/alembic_migrations/env.py
も結構いじってる
```
