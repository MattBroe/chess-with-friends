# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-30 04:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0006_auto_20170813_2110'),
    ]

    operations = [
        migrations.RenameField(
            model_name='game',
            old_name='last_move',
            new_name='last_move_source',
        ),
        migrations.AddField(
            model_name='game',
            name='last_move_target',
            field=models.CharField(default='', max_length=10),
        ),
    ]
