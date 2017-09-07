from django.contrib import admin

from .models import Game, Player
# Register your models here.

class GameAdmin(admin.ModelAdmin):
    list_display = ('pk', 'color_to_play', 'last_move_source', 'last_move_target', 'game_over', 'short_fen', 'pgn', 'status', 'draw_offered')

class PlayerAdmin(admin.ModelAdmin):
    list_display = ('pk', 'color', 'user.username', 'opponent.user.username', 'current_game.pk')


admin.site.register(Game, GameAdmin)
admin.site.register(Player)
