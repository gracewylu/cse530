# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-03-07 17:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0008_auto_20160307_1055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='class',
            name='numPrereqs',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
    ]
