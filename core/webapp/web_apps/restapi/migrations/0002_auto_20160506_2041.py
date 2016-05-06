# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.files.storage


class Migration(migrations.Migration):

    dependencies = [
        ('restapi', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fileupload',
            name='datafile',
            field=models.FileField(storage=django.core.files.storage.FileSystemStorage(location=b'/tmp/'), upload_to=b'test.txt'),
        ),
    ]
