# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-02-08 16:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coinsapp', '0007_auto_20180208_1614'),
    ]

    operations = [
        migrations.AddField(
            model_name='coinproperties',
            name='allvolume',
            field=models.FloatField(default=0),
        ),
    ]
