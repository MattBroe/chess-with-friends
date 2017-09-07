from django.test import TestCase, RequestFactory, Client
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpRequest, Http404
from .views import *
from .models import Player, Game
import json

# Create your tests here.

class PlayerTestCase(TestCase):
    
    def setUp(self):
        self.user1 = User.objects.create_user(username="Test_User_1", password="test1")
        self.user2 = User.objects.create_user(username="Test_User_2", password="test2")
        self.player1 = Player.objects.create(user=self.user1)
        self.player2 = Player.objects.create(user=self.user2)
        self.user1.save()
        self.user2.save()
        self.player1.save()
        self.player2.save()
        
    def test_user_has_player(self):
        assert hasattr(self.user1, "player"), "User instances don't have player fields"
    
    
    def test_opponent_matching(self): 
        player1_matched = self.player1.match_opponent()
        assert not player1_matched, "player1.match_opponent() was successful with no one on the waitlist"
        assert self.player1.currently_waiting, "player1.match_opponent failed, but player1 is not on the waitlist."
        player2_matched = self.player2.match_opponent()
        assert player2_matched, "Player.match_opponent() failed when the waitlist wasn't empty."
        self.player1.refresh_from_db()
        self.player2.refresh_from_db()
        assert self.player1.in_game
        assert self.player2.in_game
        assert self.player1.current_game != None
        assert self.player1.current_game == self.player2.current_game
        assert self.player1.color != self.player2.color

class ViewTestCase(TestCase):
    
    def setUp(self):
        self.user1 = User.objects.create_user(username="Test_User_1", password="test1")
        self.user2 = User.objects.create_user(username="Test_User_2", password="test2")
        self.factory = RequestFactory()

class StartGame_ViewTestCase(ViewTestCase):
    
    def test_start_game(self):
        #Test whether a user who tries to start a game and doesn't get matched is redirected home
        request = self.factory.get(reverse('start_game'))
        request.user = self.user1
        response = start_game(request)
        response.client = Client()
        self.assertRedirects(response, reverse('home'))
        
        #Test whether a user who starts a game and does get matched is redirected to their game page
        request = self.factory.get(reverse('start_game'))
        request.user = self.user2
        response = start_game(request)
        response.client = Client()
        self.assertRedirects(response, reverse('current_game_page'), target_status_code=302)

class CheckIfMatched_ViewTestCase(ViewTestCase):
    
    def test_check_if_matched(self):
        player1 = Player.objects.create(user=self.user1, in_game=True)
        player2 = Player.objects.create(user=self.user2, in_game=False)
        request = self.factory.get(reverse('check_if_matched'))
        request.user = self.user1
        response = check_if_matched(request)
        content = json.loads(response.content)
        assert content['in_game'] == True
        
        request.user = self.user2
        response = check_if_matched(request)
        content = json.loads(response.content)
        assert content['in_game'] == False

class CheckInGame_ViewTestCase(ViewTestCase):
    
    def test_check_in_game(self):
        unmatched_user = User.objects.create(username="unmatched_user", password="uuu")
        request = self.factory.get(reverse('check_in_game'))
        request.user = unmatched_user
        try:
            response = check_in_game(request)
        except Http404:
            pass
        else:
            assert False, "check_in_game doesn't 404 for a user with no player"
        
        new_player = Player.objects.create(user=unmatched_user)
        try:
            response = check_in_game(request)
        except Http404:
            pass
        else:
            assert False, "check_in_game doesn't 404 when player.in_game=False"
        
        new_player.in_game = True
        response = check_in_game(request)
        assert response.status_code == 200
        
    

#TestCases for views that require the user's player to be in a game inherit from InGameViewTestCase
class InGameViewTestCase(ViewTestCase):
    
    def setUp(self):
        self.user1 = User.objects.create_user(username="Test_User_1", password="test1")
        self.user2 = User.objects.create_user(username="Test_User_2", password="test2")
        self.factory = RequestFactory()
        self.player1 = Player.objects.create(user=self.user1)
        self.player2 = Player.objects.create(user=self.user2)
        self.player1.match_opponent()
        self.player2.match_opponent()
        self.player1.refresh_from_db()
        self.player2.refresh_from_db()
        self.game = self.player1.current_game
        

class GamePage_ViewTestCase(InGameViewTestCase):
    
    def test_game_page(self):
        request = self.factory.get(reverse('game_page', args=[self.game.pk, self.player1.color]))
        request.user = self.user1
        response = game_page(request, self.game.pk, self.player1.color)
        assert response.status_code == 200
        try:
            response = game_page(request, self.player1.current_game.pk, self.player2.color)
        except Http404:
            pass
        else:
            assert False, "game_page doesn't 404 for a player of the wrong color"
        
        
        game = Game.objects.create(pk=10)
        try:
            response = game_page(request, 10, self.player1.color)
        except Http404:
            pass
        else:
            assert False, "game_page doesn't 404 for a player trying to access the wrong game"

class CurrentGamePage_ViewTestCase(InGameViewTestCase):
    
    def test_current_game_page(self):
        request = self.factory.get(reverse('current_game_page'))
        request.user = self.user1
        response = current_game_page(request)
        response.client = Client()
        self.assertRedirects(response, reverse('game_page', args=[self.game.pk, self.player1.color]), target_status_code=302)
    
class Resign_ViewTestCase(InGameViewTestCase):
    
    def test_resign(self):
        request = self.factory.get(reverse('resign'))
        request.user = self.user1
        response = resign(request)
        self.game.refresh_from_db()
        assert response.status_code == 200
        assert self.game.game_over
        
        response = resign(request)
        assert response.status_code == 304, "Resign works when the game is over"
        
#TODO: make it so draw returns 304 when draw doesn't happen, instead of a JSON boolean

class Draw_ViewTestCase(InGameViewTestCase):
    
    def test_draw(self): 
        request = self.factory.get(reverse('draw'))
        request.user = self.user1
        response = draw(request)
        self.game.refresh_from_db()
        assert self.game.draw_offered == self.player1.color
        
        request.user = self.user2
        self.player2.current_game.refresh_from_db()
        response = draw(request)
        self.game.refresh_from_db()
        assert self.game.game_over
        assert self.game.status == "Game drawn by agreement"
    
class DeclineDraw_ViewTestCase(InGameViewTestCase):
    
    def test_decline_draw(self):
        request_draw = self.factory.get(reverse('draw'))
        request_draw.user = self.user1
        response = draw(request_draw)
        
        
        request_decline = self.factory.get(reverse('decline_draw'))
        request_decline.user = self.user2
        response = decline_draw(request_decline)
        self.game.refresh_from_db()
        assert self.game.draw_offered == "" 
        
        

    
    
    
    
        
        
        
    