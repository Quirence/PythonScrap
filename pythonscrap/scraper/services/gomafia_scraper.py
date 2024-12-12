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
        Получает HTML-страницу для игрока.
        """
        url = f"{self.BASE_URL}{self.player_id}{self.SEARCH_URL}{search_number}"
        response = requests.get(url)

        if response.status_code != 200:
            raise Exception(f"Ошибка при запросе данных для игрока {self.player_id}: HTTP {response.status_code}")

        self.html_content = response.text

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
        for i in range(2, math.ceil(
                float(self.history_total) / 10) + 1):  # Цикл проходит столько раз, сколько страниц в поиске турниров
            self.fetch_player_html(i)
            self.extract_next_data()
        self.parse_tournaments()


if __name__ == "__main__":
    player_id = 7113  # Пример ID игрока
    scraper = PlayerScraper(player_id)
    scraper.get_player_tournaments()
    print(scraper.tournaments)
