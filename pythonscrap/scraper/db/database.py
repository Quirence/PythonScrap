from scraper.services.gomafia_scraper import PlayerScraper
import os
import sqlite3
from typing import List, Dict


class DatabaseManager:
    _instance = None
    _db_name = 'user_data.db'

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

            # Получаем путь к текущей папке, где находится код, и создаём базу данных в этой папке
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'user_data.db')

            # Создаём соединение с базой данных в нужной директории
            cls._instance._conn = sqlite3.connect(db_path)
            cls._instance._conn.row_factory = sqlite3.Row  # Это позволяет доступ по имени столбца
            cls._instance._create_tables()
        return cls._instance

    def _create_tables(self):
        """Создаём необходимые таблицы, если их ещё нет."""
        cursor = self._conn.cursor()
        cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            club_id INTEGER,
            login TEXT,
            first_name TEXT,
            last_name TEXT,
            date_registration TEXT,
            icon_type TEXT,
            icon TEXT,
            gcoin INTEGER,
            elo REAL,
            vk_id INTEGER,
            referee_license INTEGER,
            is_paid INTEGER,
            is_can_comment INTEGER,
            since INTEGER,
            avatar_link TEXT DEFAULT 'Аватар отсутствует'
        );
        """)
        cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            role TEXT,
            role_translate TEXT,
            place INTEGER,
            win TEXT,
            win_translate TEXT,
            elo REAL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """)
        cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS tournaments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            date_start TEXT,
            date_end TEXT,
            country_translate TEXT,
            city_translate TEXT,
            place INTEGER,
            gg REAL,
            elo REAL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """)
        self._conn.commit()

    def insert_user_and_related_data(
            self,
            user_data: Dict,
            tournaments_data: List[Dict],
            games_data: List[Dict]
    ):
        """Основная функция для добавления пользователя и связанных с ним данных (игры и турниры), только если пользователь уникален."""

        cursor = self._conn.cursor()

        # Проверяем, существует ли уже пользователь с данным id
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_data['id'],))
        existing_user = cursor.fetchone()

        if existing_user:
            print(f"Пользователь с id {user_data['id']} уже существует в базе данных.")
            return  # Возвращаемся, не вставляя повторно

        # Вставляем данные о пользователе
        cursor.execute(""" 
        INSERT INTO users (id, club_id, login, first_name, last_name, date_registration, 
            icon_type, icon, gcoin, elo, vk_id, referee_license, is_paid, is_can_comment, 
            since, avatar_link) 
        VALUES (:id, :club_id, :login, :first_name, :last_name, :date_registration, 
            :icon_type, :icon, :gcoin, :elo, :vk_id, :referee_license, :is_paid, 
            :is_can_comment, :since, :avatar_link)
        """, user_data)

        # Вставляем игры
        if games_data is not []:
            for game in games_data:
                game['user_id'] = user_data['id']
                cursor.execute(""" 
                INSERT INTO games (user_id, role, role_translate, place, win, win_translate, elo) 
                VALUES (:user_id, :role, :role_translate, :place, :win, :win_translate, :elo)
                """, game)

        # Вставляем турниры
        if tournaments_data is not []:
            for tournament in tournaments_data:
                tournament['user_id'] = user_data['id']
                cursor.execute(""" 
                INSERT INTO tournaments (user_id, title, date_start, date_end, country_translate, 
                city_translate, place, gg, elo) 
                VALUES (:user_id, :title, :date_start, :date_end, :country_translate, 
                :city_translate, :place, :gg, :elo)
                """, tournament)

        # Подтверждаем транзакцию
        self._conn.commit()

    def get_elo_changes_by_date(self, player_id: int) -> list[tuple[str, float]]:
        """Получает массив изменений ЭЛО игрока по времени из турниров."""

        cursor = self._conn.cursor()

        # Запрашиваем данные о турнирах пользователя, включая дату и изменение ЭЛО
        cursor.execute("""
        SELECT date_start, elo 
        FROM tournaments 
        WHERE user_id = ? 
        ORDER BY date_start
        """, (player_id,))

        rows = cursor.fetchall()

        # Массив для хранения изменений ЭЛО в формате (дата, изменение ЭЛО)
        elo_changes = []

        # Пройдем по результатам и посчитаем изменения ЭЛО
        for i in range(len(rows)):
            date = rows[i]["date_start"]
            elo = rows[i]["elo"]
            elo_changes.append((date, elo))

        return elo_changes

    def get_tournaments_by_user_id(self, user_id: int) -> List[Dict]:
        """Получает массив турниров по ID игрока."""
        cursor = self._conn.cursor()

        # Запрашиваем данные о турнирах пользователя
        cursor.execute("""
        SELECT id, title, date_start, date_end, country_translate, city_translate, place, gg, elo 
        FROM tournaments
        WHERE user_id = ?
        ORDER BY date_start
        """, (user_id,))

        rows = cursor.fetchall()

        # Форматируем данные в список словарей
        tournaments = [
            {
                "id": row["id"],
                "title": row["title"],
                "date_start": row["date_start"],
                "date_end": row["date_end"],
                "country_translate": row["country_translate"],
                "city_translate": row["city_translate"],
                "place": row["place"],
                "gg": row["gg"],
                "elo": row["elo"]
            }
            for row in rows
        ]
        tournaments = sorted(tournaments, key=lambda x: int(x["id"]))

        return tournaments

    def is_player_exists(self, player_id: int) -> bool:
        """Проверяет, существует ли игрок с данным ID в базе данных."""
        cursor = self._conn.cursor()

        # Выполняем запрос на проверку наличия игрока с заданным ID
        cursor.execute("SELECT 1 FROM users WHERE id = ?", (player_id,))
        result = cursor.fetchone()

        # Если результат не пустой, значит игрок найден
        return result is not None

    def add_player_from_id(self, player_id):
        scraper = PlayerScraper(int(player_id))
        scraper.get_player_tournaments()
        user_data, tournaments_data, games_data = scraper.extract_data()
        self.insert_user_and_related_data(user_data, tournaments_data, games_data)

    def close(self):
        """Закрыть соединение с базой данных."""
        if self._conn:
            self._conn.close()
            print("Соединение с базой данных закрыто.")

# if __name__ == "__main__":
#     player_id = 6145  # Пример ID игрока
#     database = DatabaseManager()
#     print(database.is_player_exists(player_id))
