# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-26 18:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='classes',
            name='creditNum',
            field=models.SmallIntegerField(default=-1),
        ),
        migrations.AddField(
            model_name='classes',
            name='numPrereqs',
            field=models.SmallIntegerField(default=-1),
        ),
        migrations.AddField(
            model_name='classes',
            name='semOffered',
            field=models.SmallIntegerField(default=-1),
        ),
    ]
