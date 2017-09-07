import math, random
from django.db import models
from django.contrib.auth.models import User


# Create your models here.

#Player instances are created when someone clicks "Start a new game" on the homepage.

#The game model stores data which is accessed by both a player and their opponent.

long_start_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
short_start_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"

#Game instances are deleted when one of their users tries to start a new game or logs out.
#I'm planning to implement a "garbage collector" that deletes abandoned games
#after a period of inactivity.
class Game(models.Model):
    color_to_play = models.CharField(max_length=1, default="w")
    last_move_source = models.CharField(max_length=10, default="")
    last_move_target = models.CharField(max_length=10, default="")
    #Chess.js and chessboard.js use two different FEN formats
    long_fen = models.CharField(max_length=100, default=long_start_fen)
    short_fen = models.CharField(max_length=100, default=short_start_fen)
    pgn = models.CharField(max_length=300, default="")
    #Status is a text description of the game state, displayed underneath the game board
    status = models.CharField(max_length=30, default="White to move")
    #The game can end for one of three reasons: checkmate, resignation, or draw. 
    game_over = models.BooleanField(default=False)
    #If white offers a draw, draw_offered="w", and similarly for black
    draw_offered = models.CharField(max_length=1, default="")
    
        
  
class Player(models.Model):
    color = models.CharField(max_length=1, default="w")
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="player", blank=True, null=True)
    currently_waiting = models.BooleanField(default=False)
    #Note that in_game is still True even after the player's game has ended. It stays that way until
    #the game is deleted (which deletes the player via models.CASCADE)
    in_game = models.BooleanField(default=False)
    current_game = models.ForeignKey(Game, on_delete=models.CASCADE, blank=True, null=True, default=None)

    
    def match_opponent(self):
        if self.in_game == True:
            Game.objects.get(pk=self.current_game.pk).delete()
            self.in_game = False
            self.save()
        
        waitlist = Player.objects.filter(currently_waiting=True)
        waitlist = waitlist.exclude(pk=self.pk)
        num_waiting = waitlist.count()
        
        if num_waiting == 0:
            self.currently_waiting = True
            self.save()
            return 0;
        
        else:
            rand = math.floor(2*random.random())
            player1 = self
            #At any given time there is at most one player on the waitlist
            player2 = waitlist[0]
            
            player2.currently_waiting = False
            
            new_game = Game.objects.create()
            
            if rand == 0:
                player1.color = "w"
                player2.color = "b"
                
            else:
                player2.color = "w"
                player1.color = "b"
            
            player1.current_game = new_game
            player2.current_game = new_game
            player1.in_game = True
            player2.in_game = True
                
            player1.save()
            player2.save()
            new_game.save()
            
            return 1



            


        
        
        
        
            
            
            
    
