# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('node', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fabscript',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fabrun', models.CharField(max_length=255, verbose_name='fabrun')),
                ('db', models.CharField(max_length=255, verbose_name='db')),
                ('status', models.IntegerField(verbose_name='status')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True, auto_now_add=True)),
                ('node', models.ForeignKey(related_name='fabrun', verbose_name='node', to='node.Node')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='fabrun',
            name='node',
        ),
        migrations.DeleteModel(
            name='Fabrun',
        ),
    ]
