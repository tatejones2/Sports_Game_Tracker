"""
URL configuration for the API app.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.api.viewsets import (
    GameViewSet,
    LeagueViewSet,
    PlayerViewSet,
    ScoreViewSet,
    TeamViewSet,
)

# Create a router and register viewsets
router = DefaultRouter()
router.register(r"leagues", LeagueViewSet, basename="league")
router.register(r"teams", TeamViewSet, basename="team")
router.register(r"games", GameViewSet, basename="game")
router.register(r"players", PlayerViewSet, basename="player")
router.register(r"scores", ScoreViewSet, basename="score")

app_name = "api"

urlpatterns = [
    path("", include(router.urls)),
]
