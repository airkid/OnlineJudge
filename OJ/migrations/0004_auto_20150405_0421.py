# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('OJ', '0003_auto_20150405_0130'),
    ]

    operations = [
        migrations.AddField(
            model_name='problem',
            name='acceptted',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='problem',
            name='submitted',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
