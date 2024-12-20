# scraper/views.py
from django.shortcuts import render
from scraper.db.database import *
from django.utils.safestring import mark_safe
import json


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
                if database.is_player_exists(int(player_id)):
                    tournaments = database.get_tournaments_by_user_id(player_id)
                else:
                    database.add_player_from_id(player_id)
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
            if database.is_player_exists(int(player_id)):
                elo_data = database.get_elo_changes_by_date(int(player_id))  # Получаем данные эло
                print(elo_data)

                # Начальное значение эло
                current_elo = 1000

                # Обработка изменений по эло
                for date, elo_change in elo_data:
                    dates_json.append(date)
                    current_elo += elo_change  # Корректируем эло
                    elo_values_json.append(current_elo)
            else:
                status = database.add_player_from_id(int(player_id))
                if status.get("status") == "success":
                    elo_data = database.get_elo_changes_by_date(int(player_id))  # Получаем данные эло
                    print(elo_data)

                    # Начальное значение эло
                    current_elo = 1000

                    # Обработка изменений по эло
                    for date, elo_change in elo_data:
                        dates_json.append(date)
                        current_elo += elo_change  # Корректируем эло
                        elo_values_json.append(current_elo)
                else:
                    error = "Игрока с данным ID не существует, либо возникла ошибка при парсинге."
        except ValueError:
            error = "Неверный формат ID игрока. Пожалуйста, введите число."

    return render(request, 'scraper/player_elo_graph.html', {
        'player_id': player_id,
        'dates_json': dates_json,
        'elo_values_json': elo_values_json,
        'error': error
    })


def statistics_view(request):
    db = DatabaseManager()

    # Получение данных для статистики
    city_data = db.get_tournament_count_by_city()
    date_data = db.get_tournament_load_by_date()

    # Форматируем данные для передачи в шаблон
    cities_json = json.dumps([{"city": item["city"], "count": item["count"]} for item in city_data])
    dates_json = json.dumps([{"date": item["date"], "count": item["count"]} for item in date_data])

    return render(request, 'scraper/statistics.html', {
        'cities_json': mark_safe(cities_json),
        'dates_json': mark_safe(dates_json),
    })
