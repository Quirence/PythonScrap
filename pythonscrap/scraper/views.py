# scraper/views.py
from django.shortcuts import render
from .services.gomafia_scraper import *


def index(request):
    return render(request, 'scraper/main.html')


def player_tournaments(request):
    tournaments = []
    player_id = None
    error = None

    if request.method == 'POST':
        player_id = request.POST.get('player_id')
        if player_id:
            try:
                scraper = PlayerScraper(player_id)
                scraper.get_player_tournaments()
                tournaments = scraper.tournaments  # Передача данных в переменную
            except Exception as e:
                error = f"Ошибка получения данных: {str(e)}"
        else:
            error = "ID игрока не может быть пустым."

    return render(request, 'scraper/player_tournaments.html', {
        'player_id': player_id,
        'tournaments': tournaments,
        'error': error,
    })


def player_elo_graph(request):
    player_id = request.GET.get('player_id')  # Получаем ID игрока из GET-параметра
    error = None
    dates_json = []
    elo_values_json = []

    if player_id:
        try:
            player_id = int(player_id)  # Убедимся, что ID является числом
            scraper = PlayerScraper(player_id)
            scraper.get_player_tournaments()  # Получаем данные о турнирах
            elo_history = scraper.get_elo_history()
            # Извлекаем даты и значения ELO
            dates_json = [entry['date'] for entry in elo_history]
            elo_values_json = [entry['elo'] for entry in elo_history]

        except Exception as e:
            error = "Данный игрок не участвовал в турнирах ФСМ, либо его не существует."  # Если ошибка — передаем её в шаблон

    return render(request, 'scraper/player_elo_graph.html', {
        'player_id': player_id,
        'dates_json': dates_json,
        'elo_values_json': elo_values_json,
        'error': error
    })
