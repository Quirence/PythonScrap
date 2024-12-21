import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict
from scraper.services.gomafia_scraper import PlayerScraper


class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._conn = cls._create_connection()
            cls._instance._create_tables()
        return cls._instance

    @staticmethod
    def _create_connection():
        """Создаёт соединение с базой данных PostgreSQL."""
        try:
            return psycopg2.connect(
                dbname=os.getenv("POSTGRES_DB", "postgres"),
                user=os.getenv("POSTGRES_USER", "postgres"),
                password=os.getenv("POSTGRES_PASSWORD", "postgres"),
                host=os.getenv("POSTGRES_HOST", "localhost"),
                port=os.getenv("POSTGRES_PORT", "5432"),
                cursor_factory=RealDictCursor
            )
        except Exception as e:
            print("Ошибка подключения к базе данных:", str(e))
            raise

    def _create_tables(self):
        """Создаёт необходимые таблицы, если их ещё нет."""
        with self._conn.cursor() as cursor:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
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
                is_paid BOOLEAN,
                is_can_comment BOOLEAN,
                since INTEGER,
                avatar_link TEXT DEFAULT 'Аватар отсутствует'
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS games (
                id SERIAL PRIMARY KEY,
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
                id SERIAL PRIMARY KEY,
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

    def insert_user_and_related_data(self, user_data: Dict, tournaments_data: List[Dict], games_data: List[Dict]):
        """Добавление пользователя и связанных данных."""
        with self._conn.cursor() as cursor:
            # Проверяем, существует ли пользователь с данным id
            cursor.execute("SELECT id FROM users WHERE id = %s", (user_data['id'],))
            existing_user = cursor.fetchone()
            if existing_user:
                print(f"Пользователь с id {user_data['id']} уже существует в базе данных.")
                return

            # Вставляем данные о пользователе
            cursor.execute("""
            INSERT INTO users (id, club_id, login, first_name, last_name, date_registration,
                icon_type, icon, gcoin, elo, vk_id, referee_license, is_paid, is_can_comment,
                since, avatar_link) 
            VALUES (%(id)s, %(club_id)s, %(login)s, %(first_name)s, %(last_name)s, %(date_registration)s,
                %(icon_type)s, %(icon)s, %(gcoin)s, %(elo)s, %(vk_id)s, %(referee_license)s, %(is_paid)s, 
                %(is_can_comment)s, %(since)s, %(avatar_link)s)
            """, user_data)

            # Вставляем игры
            for game in games_data:
                game['user_id'] = user_data['id']
                cursor.execute("""
                INSERT INTO games (user_id, role, role_translate, place, win, win_translate, elo)
                VALUES (%(user_id)s, %(role)s, %(role_translate)s, %(place)s, %(win)s, %(win_translate)s, %(elo)s)
                """, game)

            # Вставляем турниры
            for tournament in tournaments_data:
                tournament['user_id'] = user_data['id']
                cursor.execute("""
                INSERT INTO tournaments (user_id, title, date_start, date_end, country_translate,
                city_translate, place, gg, elo) 
                VALUES (%(user_id)s, %(title)s, %(date_start)s, %(date_end)s, %(country_translate)s,
                %(city_translate)s, %(place)s, %(gg)s, %(elo)s)
                """, tournament)

        self._conn.commit()

    def get_elo_changes_by_date(self, player_id: int) -> List[tuple[str, float]]:
        """Получает массив изменений ЭЛО игрока по времени из турниров."""
        with self._conn.cursor() as cursor:
            cursor.execute("""
            SELECT date_start, elo 
            FROM tournaments 
            WHERE user_id = %s 
            ORDER BY date_start
            """, (player_id,))
            rows = cursor.fetchall()
            return [(row['date_start'], row['elo']) for row in rows]

    def get_tournaments_by_user_id(self, user_id: int) -> List[Dict]:
        """Получает массив турниров по ID игрока."""
        with self._conn.cursor() as cursor:
            cursor.execute("""
            SELECT id, title, date_start, date_end, country_translate, city_translate, place, gg, elo 
            FROM tournaments
            WHERE user_id = %s
            ORDER BY date_start
            """, (user_id,))
            return cursor.fetchall()

    def is_player_exists(self, player_id: int) -> bool:
        """Проверяет, существует ли игрок с данным ID в базе данных."""
        with self._conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM users WHERE id = %s", (player_id,))
            return cursor.fetchone() is not None

    def add_player_from_id(self, player_id):
        """Добавляет игрока в базу данных на основе ID."""
        scraper = PlayerScraper(int(player_id))
        scraper.get_player_tournaments()
        try:
            user_data, tournaments_data, games_data = scraper.extract_data()
            self.insert_user_and_related_data(user_data, tournaments_data, games_data)
            return {"status": "success"}
        except Exception as e:
            print("Ошибка при добавлении игрока:", str(e))
            return {"status": "error"}

    def get_tournament_count_by_city(self) -> List[Dict]:
        """Получает количество турниров по городам."""
        with self._conn.cursor() as cursor:
            cursor.execute("""
            SELECT city_translate, COUNT(*) as count
            FROM tournaments
            GROUP BY city_translate
            ORDER BY count DESC
            """)
            return cursor.fetchall()

    def get_tournament_load_by_date(self) -> List[Dict]:
        """Получает нагрузку по количеству турниров на каждую дату."""
        with self._conn.cursor() as cursor:
            cursor.execute("""
            SELECT date_start, COUNT(*) as count
            FROM tournaments
            GROUP BY date_start
            ORDER BY count DESC
            """)
            return cursor.fetchall()

    def get_users(self) -> List[Dict[str, str]]:
        """
        Возвращает список всех пользователей из базы данных.
        """
        with self._conn.cursor() as cursor:
            cursor.execute("SELECT id, login FROM users ORDER BY login")
            return cursor.fetchall()

    def close(self):
        """Закрыть соединение с базой данных."""
        if self._conn:
            self._conn.close()
            print("Соединение с базой данных закрыто.")
