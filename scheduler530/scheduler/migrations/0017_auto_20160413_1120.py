# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-13 16:20
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0016_auto_20160413_1119'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='school',
            name='attributes',
        ),
        migrations.RemoveField(
            model_name='school',
            name='description',
        ),
    ]
