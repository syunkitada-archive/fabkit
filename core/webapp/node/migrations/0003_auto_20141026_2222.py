# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('node', '0002_auto_20141026_1937'),
    ]

    operations = [
        migrations.AlterField(
            model_name='node',
            name='host',
            field=models.CharField(unique=True, max_length=255, verbose_name='hostname'),
            preserve_default=True,
        ),
    ]
