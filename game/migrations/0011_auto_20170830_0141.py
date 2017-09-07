# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-30 05:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0010_remove_game_pgn'),
    ]

    operations = [
        migrations.RenameField(
            model_name='game',
            old_name='fen',
            new_name='short_fen',
        ),
        migrations.AddField(
            model_name='game',
            name='long_fen',
            field=models.CharField(default='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', max_length=100),
        ),
        migrations.AddField(
            model_name='game',
            name='pgn',
            field=models.CharField(default='', max_length=200),
        ),
    ]