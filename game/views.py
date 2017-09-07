from django.shortcuts import render, redirect, get_object_or_404, Http404
from django.contrib.auth import login, authenticate
from .forms import UserCreateForm
from .models import Player, Game
from django.http import JsonResponse, HttpResponse, HttpResponseNotModified
from django.contrib.auth.decorators import login_required



# Create your views here.

#TODO: implement draw

def home(request): 
    return render(request, 'game/home.html', {})

@login_required
def start_game(request):
        
    if hasattr(request.user, 'player'):
        new_player = request.user.player
        
    else:
        new_player = Player(user=request.user)
        
    matched = new_player.match_opponent()
    
    if matched == 0:
        return redirect('home')
    
    else:
        return redirect('current_game_page')
    
@login_required
def check_if_matched(request):
    if (not hasattr(request.user, "player")):
        raise Http404("You don't have permission to access this page.")
        
    if request.method == "GET":
        pk = request.user.player.pk
        player = get_object_or_404(Player, pk=pk)
        return JsonResponse({"in_game": player.in_game})

#check_in_game is only called inside other views. No requests are sent to it directly.
@login_required
def check_in_game(request):
    if (not hasattr(request.user, "player") or 
        not request.user.player.in_game):
        raise Http404("You don't have permission to access this page.")
    
    return HttpResponse('')

@login_required
def game_page(request, pk, color):
    
    check_in_game(request)
        
    player = request.user.player
        
    game = get_object_or_404(Game, pk=pk)
    
    if player.current_game.pk != int(pk) or player.color != str(color):
        raise Http404("You don't have permission to access this page.")
    
    response = render(request, 'game/game_page.html', {"current_game": game, "player": player, "color": player.color})
    
    return response

@login_required
def current_game_page(request):
    check_in_game(request)
        
    player = request.user.player
    game = player.current_game
    return redirect('game_page', pk=game.pk, color=player.color)

@login_required
def get_current_game_info(request):
    check_in_game(request)
        
    if request.method == "GET":
        player = request.user.player
        game = player.current_game
        response = JsonResponse({"move_source": game.last_move_source, 
                             "move_target": game.last_move_target, 
                             "color_to_play": game.color_to_play,
                             "status": game.status, 
                             "game_over": game.game_over,
                             "draw_offered": game.draw_offered})
        return response
   

@login_required
def post_move(request): 
    check_in_game(request)
    
    if request.method == "POST":
        player = request.user.player
        game = player.current_game
        
        if game.game_over or game.color_to_play != player.color:
            return HttpResponse('')
    
        game.last_move_source = request.POST['move_source']
        game.last_move_target = request.POST['move_target']
        game.long_fen = request.POST['fen']
        game.short_fen = game.long_fen.split()[0]
        game.pgn = request.POST['pgn']
        game.status = request.POST['status']
        
        if player.color == "w":
            game.color_to_play = "b"
        else:
            game.color_to_play = "w"
            
        
        game.save()
        return HttpResponse('')

@login_required
def resign(request):
    check_in_game(request)
    
    if request.method == "GET":
        player = request.user.player
        game = player.current_game
        
        if game.game_over:
            #This prevents a player from resigning after their opponent has 
            #already resigned, but before their local game state updates
            return HttpResponseNotModified()
        
        if player.color == "w":
            game.status = "Black wins by resignation"
            game.color_to_play = "b"
        if player.color == "b":
            game.status = "White wins by resignation"
            game.color_to_play = "w"
        
        game.game_over = True
        
        game.save()
        return HttpResponse()

@login_required
def draw(request):
    check_in_game(request)
    
    if request.method == "GET":
        player = request.user.player
        game = player.current_game
        if game.game_over:
            return HttpResponse('')
        
        drawn = False
        if game.draw_offered == "":
            game.draw_offered = player.color
        elif game.draw_offered != player.color:
            game.game_over = True
            game.status = "Game drawn by agreement"
            drawn = True
        
        game.save()
            
        return JsonResponse({"drawn": drawn})

@login_required
def decline_draw(request):
    check_in_game(request)
        
    if request.method == "GET":
        player = request.user.player
        game = player.current_game
        if game.game_over:
            return HttpResponse('')
        game.draw_offered = ""
        game.save()
        return HttpResponse('')
    
    

def signup(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = UserCreateForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required 
def logout_user(request):
    if hasattr(request.user, 'player'):
        player = request.user.player
        if player.in_game:
            game = player.current_game
            Game.objects.get(pk=game.pk).delete()
        else:
            Player.objects.get(pk=player.pk).delete()
            
    return redirect('logout')
            
    
