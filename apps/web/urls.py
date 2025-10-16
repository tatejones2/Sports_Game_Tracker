"""
URL configuration for the web interface.
"""
from django.urls import path
from . import views

app_name = 'web'

urlpatterns = [
    # Main pages
    path('', views.dashboard, name='dashboard'),
    path('live/', views.live_games, name='live_games'),
    path('schedule/', views.schedule, name='schedule'),
    path('standings/', views.standings, name='standings'),
    path('team/<int:team_id>/', views.team_detail, name='team_detail'),
    path('game/<int:game_id>/', views.game_detail, name='game_detail'),
    
    # HTMX API endpoints for partial updates
    path('api/live-count/', views.api_live_count, name='api_live_count'),
    path('api/live-games/', views.api_live_games, name='api_live_games'),
]
