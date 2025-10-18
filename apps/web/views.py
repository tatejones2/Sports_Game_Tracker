"""
Views for the web interface.
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from django.db import models
from datetime import datetime, date
from apps.core.models import Game, League, Team


def dashboard(request):
    """
    Main dashboard showing overview of live games, today's schedule, and quick stats.
    """
    today = timezone.localtime(timezone.now()).date()
    
    # Get counts for stats cards
    live_count = Game.objects.filter(status='live').count()
    today_count = Game.objects.filter(game_date__date=today).count()
    teams_count = Team.objects.count()
    leagues_count = League.objects.count()
    
    # Get today's games
    today_games = Game.objects.filter(
        game_date__date=today
    ).select_related(
        'home_team', 'away_team', 'league'
    ).order_by('scheduled_time')
    
    context = {
        'live_count': live_count,
        'today_count': today_count,
        'teams_count': teams_count,
        'leagues_count': leagues_count,
        'today_games': today_games,
    }
    
    return render(request, 'web/dashboard.html', context)


def api_live_count(request):
    """
    HTMX endpoint for live game count (auto-refreshing).
    """
    from django.http import HttpResponse
    count = Game.objects.filter(status='live').count()
    return HttpResponse(str(count))


def api_live_games(request):
    """
    HTMX endpoint for live games partial (auto-refreshing).
    """
    live_games = Game.objects.filter(
        status='live'
    ).select_related(
        'home_team', 'away_team', 'league'
    ).order_by('scheduled_time')
    
    return render(request, 'web/partials/_live_games.html', {
        'live_games': live_games
    })


def live_games(request):
    """
    Full page showing all live games with auto-refresh.
    """
    live_games = Game.objects.filter(
        status='live'
    ).select_related(
        'home_team', 'away_team', 'league'
    ).order_by('scheduled_time')
    
    context = {
        'live_games': live_games,
    }
    
    return render(request, 'web/live_games.html', context)


def schedule(request):
    """
    Schedule page showing games by date with filtering options.
    """
    # Get date from query param or default to today
    date_str = request.GET.get('date')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = timezone.localtime(timezone.now()).date()
    else:
        selected_date = timezone.localtime(timezone.now()).date()
    
    # Get league filter
    league_id = request.GET.get('league')
    
    # Build query
    games_query = Game.objects.filter(
        game_date__date=selected_date
    ).select_related('home_team', 'away_team', 'league')
    
    if league_id:
        games_query = games_query.filter(league_id=league_id)
    
    games = games_query.order_by('scheduled_time')
    
    # Get all leagues for filter dropdown
    leagues = League.objects.all().order_by('name')
    
    context = {
        'games': games,
        'selected_date': selected_date,
        'leagues': leagues,
        'selected_league_id': int(league_id) if league_id else None,
    }
    
    return render(request, 'web/schedule.html', context)


def standings(request):
    """
    Standings page showing team records by league.
    """
    # Get league filter or default to first league
    league_id = request.GET.get('league')
    
    leagues = League.objects.all().order_by('name')
    
    if league_id:
        selected_league = League.objects.filter(id=league_id).first()
    else:
        selected_league = leagues.first()
    
    # Get teams for selected league with their records
    teams = []
    if selected_league:
        teams = Team.objects.filter(
            league=selected_league
        ).order_by('-wins', 'losses', 'name')
    
    context = {
        'leagues': leagues,
        'selected_league': selected_league,
        'teams': teams,
    }
    
    return render(request, 'web/standings.html', context)


def team_detail(request, team_id):
    """
    Team detail page showing team info, roster, and recent/upcoming games.
    """
    team = Team.objects.select_related('league').get(id=team_id)
    
    # Get recent games (last 5 completed)
    recent_games = Game.objects.filter(
        status='final'
    ).filter(
        home_team=team
    ) | Game.objects.filter(
        status='final'
    ).filter(
        away_team=team
    )
    recent_games = recent_games.select_related(
        'home_team', 'away_team', 'league'
    ).order_by('-game_date', '-scheduled_time')[:5]
    
    # Get upcoming games (next 5)
    upcoming_games = Game.objects.filter(
        status='scheduled',
        game_date__gte=timezone.now().date()
    ).filter(
        home_team=team
    ) | Game.objects.filter(
        status='scheduled',
        game_date__gte=timezone.now().date()
    ).filter(
        away_team=team
    )
    upcoming_games = upcoming_games.select_related(
        'home_team', 'away_team', 'league'
    ).order_by('game_date', 'scheduled_time')[:5]
    
    # Get roster
    roster = team.players.all().order_by('jersey_number')
    
    context = {
        'team': team,
        'recent_games': recent_games,
        'upcoming_games': upcoming_games,
        'roster': roster,
    }
    
    return render(request, 'web/team_detail.html', context)


def game_detail(request, game_id):
    """
    Game detail page showing period-by-period scores and game info.
    """
    game = Game.objects.select_related(
        'home_team', 'away_team', 'league'
    ).get(id=game_id)
    
    # Get period scores
    scores = game.scores.all().order_by('period')
    
    # Organize scores by period
    periods = []
    max_period = scores.aggregate(max_period=models.Max('period'))['max_period'] or 0
    
    for period_num in range(1, max_period + 1):
        home_score = scores.filter(team=game.home_team, period=period_num).first()
        away_score = scores.filter(team=game.away_team, period=period_num).first()
        
        periods.append({
            'period': period_num,
            'home_score': home_score.points if home_score else 0,
            'away_score': away_score.points if away_score else 0,
        })
    
    context = {
        'game': game,
        'periods': periods,
    }
    
    return render(request, 'web/game_detail.html', context)
