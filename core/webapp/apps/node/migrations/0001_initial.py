# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('path', models.CharField(default='', unique=True, max_length=255)),
                ('data', models.CharField(default='{}', max_length=10000)),
                ('status', models.IntegerField(default=0)),
                ('msg', models.CharField(default='', max_length=1024)),
                ('logs', models.CharField(default='[]', max_length=1024)),
                ('logs_all', models.CharField(default='[]', max_length=1024)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True, auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NodeCluster',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default='', unique=True, max_length=255)),
                ('data', models.CharField(default='{}', max_length=100000)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True, auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='node',
            name='cluster',
            field=models.ForeignKey(to='node.NodeCluster', null=True),
            preserve_default=True,
        ),
    ]
