from django.urls import path
from . import views

urlpatterns = [
    path('player_tournaments/', views.player_tournaments, name='player_tournaments'),
]
