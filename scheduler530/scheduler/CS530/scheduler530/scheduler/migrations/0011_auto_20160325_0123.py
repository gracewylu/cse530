# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-03-25 06:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0010_school_creditstograduate'),
    ]

    operations = [
        migrations.AddField(
            model_name='class',
            name='classStanding',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='class',
            name='deptID',
            field=models.CharField(max_length=4),
        ),
    ]
