# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('OJ', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submit',
            name='code',
        ),
        migrations.AlterField(
            model_name='submit',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(0, 'UNKNOWN'), (1, 'C'), (2, 'C++'), (3, 'Java'), (4, 'Python'), (5, 'Pascal'), (6, 'FORTRAN')]),
        ),
    ]
