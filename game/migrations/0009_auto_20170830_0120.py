# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-30 05:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0008_game_fen'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='pgn',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AlterField(
            model_name='game',
            name='fen',
            field=models.CharField(default='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR', max_length=100),
        ),
    ]
