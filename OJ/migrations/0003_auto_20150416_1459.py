# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('OJ', '0002_auto_20150406_1459'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestCase',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('sample', models.BooleanField(default=False)),
                ('input', models.TextField()),
                ('output', models.TextField()),
            ],
            options={
                'ordering': ['time'],
            },
        ),
        migrations.RemoveField(
            model_name='answer',
            name='pid',
        ),
        migrations.RemoveField(
            model_name='answer',
            name='uid',
        ),
        migrations.AddField(
            model_name='problem',
            name='answer_type',
            field=models.PositiveSmallIntegerField(choices=[(0, 'UNKNOWN'), (1, 'C'), (2, 'C++'), (3, 'Java'), (4, 'Python'), (5, 'Pascal'), (6, 'FORTRAN')], default=1),
        ),
        migrations.AlterField(
            model_name='problem',
            name='limit_time',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='submit',
            name='status',
            field=models.SmallIntegerField(choices=[(0, 'Accepted'), (1, 'Waiting'), (2, 'Compiling'), (3, 'Running'), (-1, 'Compilation Error'), (-2, 'Syntax Error'), (-3, 'Runtime Error'), (-4, 'Output Limit Exceeded'), (-5, 'Time Limit Exceeded'), (-6, 'Memory Limit Exceeded'), (-7, 'Wrong Answer'), (-8, 'Presentation Error')], default=1),
        ),
        migrations.DeleteModel(
            name='Answer',
        ),
        migrations.AddField(
            model_name='testcase',
            name='pid',
            field=models.ForeignKey(to='OJ.Problem'),
        ),
        migrations.AddField(
            model_name='testcase',
            name='uid',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
