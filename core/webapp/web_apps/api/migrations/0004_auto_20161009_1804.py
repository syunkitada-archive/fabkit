# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.files.storage
import web_apps.api.models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20160514_1805'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='file',
            field=models.FileField(storage=django.core.files.storage.FileSystemStorage(location=b'/home/owner/fabkit-repo/storage/webapp'), upload_to=web_apps.api.models.upload_to),
        ),
    ]
