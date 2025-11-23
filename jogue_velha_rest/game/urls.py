"""
URLs do app game
"""
from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    path('room/join', views.join_room, name='join_room'),
    path('room/move', views.make_move, name='make_move'),
    path('room/state', views.get_room_state, name='get_room_state'),
    path('health', views.health_check, name='health_check'),
]
