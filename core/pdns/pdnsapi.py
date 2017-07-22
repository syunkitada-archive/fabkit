# coding: utf-8

import datetime
from oslo_config import cfg
from oslo_db.sqlalchemy import session as db_session
from sqlalchemy.orm import exc
from sqlalchemy import desc
from impl_sqlalchemy import models
from fabkit import util
from oslo_log import log as logging

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class PdnsAPI():

    def __init__(self, url=None):
        options = dict(CONF.pdns_database.items())
        if url is None:
            url = options['connection']
        self.engine_facade = db_session.EngineFacade(url, **options)
        self.session = self.engine_facade.get_session()

    def get_session(self):
        return self.session

    def get_domain(self, name):
        query = self.session.query(models.Domains)
        domain = query.filter(models.Domains.name == name).one()
        return domain

    def get_domains(self):
        query = self.session.query(models.Domains)
        domains = query.all()
        return domains

    def create_domain(self, name, type='NATIVE'):
        with self.session.begin():
            try:
                domain = self.get_domain(name)

            except exc.NoResultFound:
                domain = models.Domains(name=name, type=type)
                self.session.add(domain)

        with self.session.begin():
            domain = self.get_domain(name)
            soa = 'localhost admin.example.com 1 10380 3600 604800 3600'
            ns = 'localhost'
            soa_record = models.Records(
                domain_id=domain.id, name=name, content=soa, type='SOA', ttl=86400, prio=None)
            ns_record = models.Records(
                domain_id=domain.id, name=name, content=ns, type='NS', ttl=86400, prio=None)
            self.session.add(soa_record)
            self.session.add(ns_record)

    def delete_domain(self, name):
        query = self.session.query(models.Records)

        with self.session.begin():
            query.filter(models.Records.name == name)

    def get_record(self, name):
        query = self.session.query(models.Records)
        record = query.filter(models.Records.name == name).one()
        return record

    def get_records(self, domain_id):
        query = self.session.query(models.Records)
        records = query.all()
        return records

    def create_record(self, name, domain_name, type, content, ttl=120, prio=None):
        with self.session.begin():
            name = '{0}.{1}'.format(name, domain_name)
            try:
                record = self.get_record(name)

            except exc.NoResultFound:
                domain = self.get_domain(domain_name)
                record = models.Records(domain_id=domain.id, name=name, content=content, type=type, ttl=ttl, prio=prio)
                self.session.add(record)

    def delete_record(self, name):
        query = self.session.query(models.Records)

        with self.session.begin():
            query.filter(models.Records.name == name)
