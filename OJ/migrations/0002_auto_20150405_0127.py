# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('OJ', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='note',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='problem',
            name='source',
            field=models.TextField(null=True),
        ),
    ]
