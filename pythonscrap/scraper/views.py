# scraper/views.py
from django.shortcuts import render
from .db.database import *


def index(request):
    return render(request, 'scraper/main.html')


def player_tournaments(request):
    tournaments = []
    player_id = None
    error = None
    database = DatabaseManager()
    if request.method == 'POST':
        player_id = request.POST.get('player_id')
        if player_id:
            try:
                tournaments = database.get_tournaments_by_user_id(player_id)
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
    database = DatabaseManager()
    error = None
    dates_json = []
    elo_values_json = []

    player_id = request.GET.get('player_id')  # Получаем ID игрока из GET-запроса

    if player_id:
        try:
            player_id = int(player_id)  # Преобразуем ID в число
            elo_data = database.get_elo_changes_by_date(int(player_id))  # Получаем данные эло
            print(elo_data)

            # Начальное значение эло
            current_elo = 1000

            # Обработка изменений по эло
            for date, elo_change in elo_data:
                dates_json.append(date)
                current_elo += elo_change  # Корректируем эло
                elo_values_json.append(current_elo)
        except ValueError:
            error = "Неверный формат ID игрока. Пожалуйста, введите число."

    return render(request, 'scraper/player_elo_graph.html', {
        'player_id': player_id,
        'dates_json': dates_json,
        'elo_values_json': elo_values_json,
        'error': error
    })
