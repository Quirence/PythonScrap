import os
import sqlite3
from typing import List, Dict
from scraper.services.gomafia_scraper import PlayerScraper


class DatabaseManager:
    _instance = None
    _db_name = 'user_data.db'

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'user_data.db')
            cls._instance._conn = sqlite3.connect(db_path, check_same_thread=False)
            cls._instance._conn.row_factory = sqlite3.Row
            cls._instance._create_tables()
        return cls._instance

    def _create_tables(self):
        """Создаём необходимые таблицы, если их ещё нет."""
        with self._conn as conn:
            cursor = conn.cursor()
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

    def insert_user_and_related_data(self, user_data: Dict, tournaments_data: List[Dict], games_data: List[Dict]):
        """Добавление пользователя и связанных данных."""
        with self._conn as conn:
            cursor = conn.cursor()

            # Проверяем, существует ли пользователь с данным id
            cursor.execute("SELECT id FROM users WHERE id = ?", (user_data['id'],))
            existing_user = cursor.fetchone()
            if existing_user:
                print(f"Пользователь с id {user_data['id']} уже существует в базе данных.")
                return

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
            for game in games_data:
                game['user_id'] = user_data['id']
                cursor.execute("""
                INSERT INTO games (user_id, role, role_translate, place, win, win_translate, elo)
                VALUES (:user_id, :role, :role_translate, :place, :win, :win_translate, :elo)
                """, game)

            # Вставляем турниры
            for tournament in tournaments_data:
                tournament['user_id'] = user_data['id']
                cursor.execute("""
                INSERT INTO tournaments (user_id, title, date_start, date_end, country_translate,
                city_translate, place, gg, elo) 
                VALUES (:user_id, :title, :date_start, :date_end, :country_translate,
                :city_translate, :place, :gg, :elo)
                """, tournament)

    def get_elo_changes_by_date(self, player_id: int) -> List[tuple[str, float]]:
        """Получает массив изменений ЭЛО игрока по времени из турниров."""
        with self._conn as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT date_start, elo 
            FROM tournaments 
            WHERE user_id = ? 
            ORDER BY date_start
            """, (player_id,))
            rows = cursor.fetchall()
            return [(row["date_start"], row["elo"]) for row in rows]

    def get_tournaments_by_user_id(self, user_id: int) -> List[Dict]:
        """Получает массив турниров по ID игрока."""
        with self._conn as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT id, title, date_start, date_end, country_translate, city_translate, place, gg, elo 
            FROM tournaments
            WHERE user_id = ?
            ORDER BY date_start
            """, (user_id,))
            rows = cursor.fetchall()
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
        with self._conn as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM users WHERE id = ?", (player_id,))
            return cursor.fetchone() is not None

    def add_player_from_id(self, player_id):
        """Добавляет игрока в базу данных на основе ID."""
        scraper = PlayerScraper(int(player_id))
        scraper.get_player_tournaments()
        user_data, tournaments_data, games_data = scraper.extract_data()
        self.insert_user_and_related_data(user_data, tournaments_data, games_data)

    def close(self):
        """Закрыть соединение с базой данных."""
        if self._conn:
            self._conn.close()
            print("Соединение с базой данных закрыто.")
