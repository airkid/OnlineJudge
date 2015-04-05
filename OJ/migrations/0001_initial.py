# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('example', models.BooleanField(default=False)),
                ('input', models.TextField()),
                ('output', models.TextField()),
            ],
            options={
                'ordering': ['time'],
            },
        ),
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('limit_time', models.PositiveIntegerField(default=1000)),
                ('limit_memory', models.PositiveIntegerField(default=134217728)),
                ('title', models.CharField(max_length=254)),
                ('content', models.TextField()),
                ('input', models.TextField()),
                ('output', models.TextField()),
                ('note', models.TextField()),
                ('source', models.TextField()),
            ],
            options={
                'ordering': ['time'],
            },
        ),
        migrations.CreateModel(
            name='Submit',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('type', models.SmallIntegerField(choices=[(1, 'C'), (2, 'C++'), (3, 'Java'), (4, 'Python'), (5, 'Pascal'), (6, 'FORTRAN')])),
                ('code', models.FileField(upload_to='submit')),
                ('status', models.SmallIntegerField(choices=[(0, 'Accepted'), (1, 'Waiting'), (2, 'Compiling'), (-1, 'Compilation Error'), (-2, 'Wrong Answer'), (-3, 'Presentation Error'), (-4, 'Output Limit Exceeded'), (-5, 'Time Limit Exceeded'), (-6, 'Memory Limit Exceeded'), (-7, 'Runtime Error')], default=1)),
                ('run_time', models.PositiveSmallIntegerField(null=True)),
                ('run_memory', models.PositiveIntegerField(null=True)),
                ('pid', models.ForeignKey(to='OJ.Problem')),
            ],
            options={
                'ordering': ['time'],
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
                ('pw', models.CharField(max_length=86)),
                ('email', models.EmailField(max_length=254)),
                ('time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['time'],
            },
        ),
        migrations.AddField(
            model_name='submit',
            name='uid',
            field=models.ForeignKey(to='OJ.User'),
        ),
        migrations.AddField(
            model_name='problem',
            name='uid',
            field=models.ForeignKey(to='OJ.User'),
        ),
        migrations.AddField(
            model_name='answer',
            name='pid',
            field=models.ForeignKey(to='OJ.Problem'),
        ),
        migrations.AddField(
            model_name='answer',
            name='uid',
            field=models.ForeignKey(to='OJ.User'),
        ),
    ]
