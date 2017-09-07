from django.conf.urls import url
from . import views

urlpatterns = [
        url(r'^$', views.home, name='home'),
        url(r'^signup/$', views.signup, name='signup'),
        url(r'^start_game', views.start_game, name='start_game'),
        url(r'^game/(?P<pk>\d+)/(?P<color>[wb])/$', views.game_page, name='game_page'),
        url(r'^logout/$', views.logout_user, name='logout_user'),
        url(r'^check_if_matched', views.check_if_matched, name='check_if_matched'),
        url(r'^current_game_page', views.current_game_page, name='current_game_page'),
        url(r'^get_current_game_info', views.get_current_game_info, name='get_current_game_info'),
        url(r'^post_move', views.post_move, name='post_move'),
        url(r'^resign', views.resign, name='resign'),
        url(r'^draw', views.draw, name='draw'),
        url(r'^decline_draw', views.decline_draw, name='decline_draw'),
        url(r'^check_in_game', views.check_in_game, name='check_in_game'),
        ]
