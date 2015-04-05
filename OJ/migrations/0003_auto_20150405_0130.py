# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('OJ', '0002_auto_20150405_0127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='note',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='problem',
            name='source',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
    ]
