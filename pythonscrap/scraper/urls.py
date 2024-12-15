from django.urls import path
from . import views

urlpatterns = [
    path('player_tournaments/', views.player_tournaments, name='player_tournaments'),
    path('player/elo-chart/', views.player_elo_graph, name='player_elo_graph'),
    path('', views.index, name='index'),
]
