# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Fabrun',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fabrun', models.CharField(max_length=255, verbose_name='fabrun')),
                ('status', models.IntegerField(verbose_name='status')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True, auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('host', models.CharField(max_length=255, verbose_name='hostname')),
                ('ip', models.CharField(max_length=255, verbose_name='ip')),
                ('uptime', models.CharField(max_length=255, verbose_name='uptime')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True, auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='fabrun',
            name='node',
            field=models.ForeignKey(related_name='fabrun', verbose_name='node', to='node.Node'),
            preserve_default=True,
        ),
    ]
