import requests
from bs4 import BeautifulSoup
import json
import math


class PlayerScraper:
    BASE_URL = "https://gomafia.pro/stats/"
    SEARCH_URL = "?tab=history&page="

    def __init__(self, player_id):
        """
        Инициализация скраппера с указанным ID игрока.
        """
        self.player_id = player_id
        self.html_content = None
        self.next_data = []
        self.history_total = None  # Количество турниров, в которых игрок принимал участие
        self.tournaments = []

    def fetch_player_html(self, search_number=1):
        """
        Получает HTML-страницу для игрока и проверяет, существует ли он.
        """
        url = f"{self.BASE_URL}{self.player_id}{self.SEARCH_URL}{search_number}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Ошибка при запросе данных для игрока {self.player_id}: HTTP {response.status_code}")

        self.html_content = response.text

        # Проверка на наличие текста, указывающего на отсутствие игрока
        if "Игрок не найден" in self.html_content or "No player found" in self.html_content:
            raise Exception(f"Игрок с ID {self.player_id} не существует на сайте.")

    def extract_next_data(self):
        """
        Извлекает JSON из тега <script id="__NEXT_DATA__"> из HTML-страницы.
        """
        if not self.html_content:
            raise Exception("HTML-контент не был загружен. Сначала вызовите fetch_player_html.")

        soup = BeautifulSoup(self.html_content, "html.parser")
        script_tag = soup.find("script", id="__NEXT_DATA__")

        if not script_tag:
            raise Exception("Тег <script id='__NEXT_DATA__'> не найден на странице")

        try:
            self.next_data.append(json.loads(script_tag.string))
        except json.JSONDecodeError:
            raise Exception("Ошибка при парсинге JSON из __NEXT_DATA__")

    def parse_history_number(self):
        """
        Извлекает данные о количестве из JSON (__NEXT_DATA__).
        """
        if not self.next_data:
            raise Exception("JSON данные не были извлечены. Сначала вызовите extract_next_data.")

        self.history_total = self.next_data[0].get("props", {}).get("pageProps", {}).get("serverData", {}).get(
            "historyTotal")

    def parse_tournaments(self):
        """
        Извлекает данные о турнирах из JSON (__NEXT_DATA__).
        """
        if not self.next_data:
            raise Exception("JSON данные не были извлечены. Сначала вызовите extract_next_data.")
        for next_data in self.next_data:
            history_data = next_data.get("props", {}).get("pageProps", {}).get("serverData", {}).get("history", [])
            if history_data is not None:
                for tournament in history_data:
                    tournament_info = {
                        "id": tournament.get("id"),
                        "title": tournament.get("title"),
                        "date_start": tournament.get("date_start"),
                        "date_end": tournament.get("date_end"),
                        "place": tournament.get("place"),
                        "elo": tournament.get("elo"),
                    }
                    self.tournaments.append(tournament_info)
            else:
                self.tournaments = ["Данный игрок не участвовал в турнирах ФСМ."]

    def get_player_tournaments(self):
        """
        Главный метод: выполняет полный цикл для получения турниров игрока.
        """
        self.fetch_player_html()
        self.extract_next_data()
        self.parse_history_number()
        if self.history_total is not None:
            for i in range(2, math.ceil(
                    float(
                        self.history_total) / 10) + 1):  # Цикл проходит столько раз, сколько страниц в поиске турниров
                self.fetch_player_html(i)
                self.extract_next_data()
        self.parse_tournaments()

    def extract_data(self):
        """
        Извлекает данные о пользователе, турнирах и играх с проверками на наличие ключей и данных.
        """
        user_data = self.next_data[0].get('props', {}).get('pageProps', {}).get('serverData', {}).get('user', {})

        # Проверка, если данных о пользователе нет
        if not user_data:
            raise Exception(f"Данные о пользователе для игрока с ID {self.player_id} не найдены.")

        # Обрабатываем отсутствие аватара
        avatar_link = user_data.get('avatar_link', None)
        if avatar_link is None:
            user_data['avatar_link'] = 'Аватар отсутствует'

        print(f"Данные о пользователе: {user_data}")

        tournaments_data = []
        games_data = []

        # Проверяем наличие истории турниров
        for data in self.next_data:
            server_data = data.get('props', {}).get('pageProps', {}).get('serverData', {})

            if not server_data:
                print(f"Нет данных для страницы с ID {self.player_id}. Пропускаем.")
                continue

            tournament_history = server_data.get('history', [])

            # Если турниров нет, добавляем сообщение о том, что игрок не участвовал в турнирах
            if not tournament_history:
                print(f"Игрок с ID {self.player_id} не участвовал в турнирах.")
                continue

            for tournament in tournament_history:
                tournament_info = {
                    'id': tournament.get('id', 'Неизвестно'),
                    'title': tournament.get('title', 'Неизвестно'),
                    'date_start': tournament.get('date_start', 'Неизвестно'),
                    'date_end': tournament.get('date_end', 'Неизвестно'),
                    'country_translate': tournament.get('country_translate', 'Неизвестно'),
                    'city_translate': tournament.get('city_translate', 'Неизвестно'),
                    'place': tournament.get('place', 'Неизвестно'),
                    'gg': tournament.get('gg', 'Неизвестно'),
                    'elo': tournament.get('elo', 'Неизвестно')
                }
                tournaments_data.append(tournament_info)

                # Данные о играх в турнире
                games = tournament.get('games', [])
                if games:
                    for game in games:
                        game_info = {
                            'role': game.get('role', 'Неизвестно'),
                            'role_translate': game.get('role_translate', 'Неизвестно'),
                            'place': game.get('place', 'Неизвестно'),
                            'win': game.get('win', 'Неизвестно'),
                            'win_translate': game.get('win_translate', 'Неизвестно'),
                            'elo': game.get('elo', 'Неизвестно')
                        }
                        games_data.append(game_info)

        return user_data, tournaments_data, games_data


def simplify_dict(d):
    """
    Упрощает словарь, оставляя одно значение для каждого ключа.
    Если значение - вложенный словарь, обрабатывает его рекурсивно.
    """
    if isinstance(d, dict):
        # Если значение - словарь, упрощаем его рекурсивно
        return {k: simplify_dict(v) for k, v in d.items()}
    elif isinstance(d, list):
        # Если значение - список, оставляем первый элемент
        return simplify_dict(d[0]) if d else None
    else:
        # Если это не список и не словарь, оставляем как есть
        return d

# if __name__ == "__main__":
#     scraper = PlayerScraper(6146)
#     scraper.get_player_tournaments()
#     user_data, tournaments_data, games_data = scraper.extract_data()
#     print(tournaments_data)
