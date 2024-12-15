import sqlite3
from typing import Dict, Any, List


class DatabaseSingleton:
    """
    Синглтон для работы с базой данных SQLite.
    """
    _instance = None

    def __new__(cls, db_name: str):
        if cls._instance is None:
            cls._instance = super(DatabaseSingleton, cls).__new__(cls)
            cls._instance.connection = sqlite3.connect(db_name, check_same_thread=False)
            cls._instance.cursor = cls._instance.connection.cursor()
        return cls._instance

    def execute(self, query: str, params: tuple = ()):
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"SQLite error: {e} - Query: {query} - Params: {params}")

    def fetchall(self, query: str, params: tuple = ()) -> List[Any]:
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def fetchone(self, query: str, params: tuple = ()) -> Any:
        self.cursor.execute(query, params)
        return self.cursor.fetchone()


class DatabaseManager:
    """
    Менеджер для работы с таблицами базы данных.
    """

    def __init__(self, db_name: str):
        self.db = DatabaseSingleton(db_name)

    def insert_or_update_user(self, user_data: Dict[str, Any]):
        query_check = "SELECT id FROM users WHERE id = ?"
        existing_user = self.db.fetchone(query_check, (user_data['id'],))

        if existing_user:
            query_update = """
                UPDATE users SET
                    club_id = ?, login = ?, first_name = ?, last_name = ?, 
                    date_registration = ?, icon_type = ?, icon = ?, gcoin = ?, 
                    elo = ?, vk_id = ?, referee_license = ?, is_paid = ?, 
                    is_can_comment = ?, since = ?, avatar_link = ?, average_elo = ?
                WHERE id = ?
            """
            self.db.execute(query_update, (
                user_data['club_id'], user_data['login'], user_data['first_name'], user_data['last_name'],
                user_data['date_registration'], user_data['icon_type'], user_data['icon'], user_data['gcoin'],
                user_data['elo'], user_data['vk_id'], user_data['referee_license'], user_data['is_paid'],
                user_data['is_can_comment'], user_data['since'], user_data['avatar_link'], user_data['average_elo'],
                user_data['id']
            ))
        else:
            query_insert = """
                INSERT INTO users (id, club_id, login, first_name, last_name, 
                                   date_registration, icon_type, icon, gcoin, elo, 
                                   vk_id, referee_license, is_paid, is_can_comment, 
                                   since, avatar_link, average_elo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            self.db.execute(query_insert, (
                user_data['id'], user_data['club_id'], user_data['login'], user_data['first_name'],
                user_data['last_name'],
                user_data['date_registration'], user_data['icon_type'], user_data['icon'], user_data['gcoin'],
                user_data['elo'],
                user_data['vk_id'], user_data['referee_license'], user_data['is_paid'], user_data['is_can_comment'],
                user_data['since'], user_data['avatar_link'], user_data['average_elo']
            ))

    def insert_or_update_stat(self, user_id: int, stat_data: Dict[str, Any]):
        query_check = "SELECT id FROM stats WHERE user_id = ? AND role = ?"
        for role, role_data in stat_data.items():
            if role != 'total_games' and role != 'total_wins':  # Пропускаем неигровые данные
                existing_stat = self.db.fetchone(query_check, (user_id, role))

                if existing_stat:
                    query_update = """
                        UPDATE stats SET
                            total_games = ?, wins = ?, win_percent = ?, max_win_streak = ?, average_points = ?, 
                            prize_places = ?
                        WHERE user_id = ? AND role = ?
                    """
                    self.db.execute(query_update, (
                        role_data['total']['value'], role_data['win']['value'], role_data['win']['percent'],
                        stat_data['win_strike'][role]['max'], stat_data['games_stats']['average_points'],
                        stat_data['games_stats']['prize_places'], user_id, role
                    ))
                else:
                    query_insert = """
                        INSERT INTO stats (user_id, role, total_games, wins, win_percent, max_win_streak, 
                                           average_points, prize_places)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    self.db.execute(query_insert, (
                        user_id, role, role_data['total']['value'], role_data['win']['value'],
                        role_data['win']['percent'],
                        stat_data['win_strike'][role]['max'], stat_data['games_stats']['average_points'],
                        stat_data['games_stats']['prize_places']
                    ))

    def insert_or_update_tournament(self, user_id: int, tournament_data: Dict[str, Any]):
        query_check = "SELECT id FROM tournaments WHERE id = ?"
        existing_tournament = self.db.fetchone(query_check, (tournament_data['id'],))

        if existing_tournament:
            query_update = """
                UPDATE tournaments SET
                    user_id = ?, title = ?, date_start = ?, date_end = ?, country = ?, 
                    city = ?, place = ?, gg = ?, elo_change = ?
                WHERE id = ?
            """
            self.db.execute(query_update, (
                user_id, tournament_data['title'], tournament_data['date_start'], tournament_data['date_end'],
                tournament_data['country_translate'], tournament_data['city_translate'], tournament_data['place'],
                tournament_data['gg'], tournament_data['elo'], tournament_data['id']
            ))
        else:
            query_insert = """
                INSERT INTO tournaments (id, user_id, title, date_start, date_end, country, 
                                         city, place, gg, elo_change)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            self.db.execute(query_insert, (
                tournament_data['id'], user_id, tournament_data['title'], tournament_data['date_start'],
                tournament_data['date_end'], tournament_data['country_translate'], tournament_data['city_translate'],
                tournament_data['place'], tournament_data['gg'], tournament_data['elo']
            ))

    def insert_or_update_tournament_game(self, game_data: Dict[str, Any]):
        query_check = "SELECT id FROM tournament_games WHERE tournament_id = ? AND game_num = ?"
        existing_game = self.db.fetchone(query_check, (game_data['tournament_id'], game_data['game_num']))

        if existing_game:
            query_update = """
                UPDATE tournament_games SET
                    role = ?, place = ?, win = ?, win_translate = ?, elo_change = ?
                WHERE tournament_id = ? AND game_num = ?
            """
            self.db.execute(query_update, (
                game_data['role'], game_data['place'], game_data['win'],
                game_data['win_translate'], game_data['elo_change'],
                game_data['tournament_id'], game_data['game_num']
            ))
        else:
            query_insert = """
                INSERT INTO tournament_games (tournament_id, game_num, role, place, win, win_translate, elo_change)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            self.db.execute(query_insert, (
                game_data['tournament_id'], game_data['game_num'], game_data['role'],
                game_data['place'], game_data['win'], game_data['win_translate'],
                game_data['elo_change']
            ))

    def insert_or_update_elo_history(self, history_data: Dict[str, Any]):
        query_check = "SELECT id FROM elo_history WHERE user_id = ? AND tournament_id = ? AND date = ?"
        existing_history = self.db.fetchone(query_check, (
            history_data['user_id'], history_data['tournament_id'], history_data['date']))

        if existing_history:
            query_update = """
                UPDATE elo_history SET
                    elo = ?, elo_delta = ?
                WHERE user_id = ? AND tournament_id = ? AND date = ?
            """
            self.db.execute(query_update, (
                history_data['elo'], history_data['elo_delta'],
                history_data['user_id'], history_data['tournament_id'], history_data['date']
            ))
        else:
            query_insert = """
                INSERT INTO elo_history (user_id, tournament_id, date, elo, elo_delta)
                VALUES (?, ?, ?, ?, ?)
            """
            self.db.execute(query_insert, (
                history_data['user_id'], history_data['tournament_id'], history_data['date'],
                history_data['elo'], history_data['elo_delta']
            ))

    def insert_or_update_default_params(self, params_data: Dict[str, Any]):
        query_check = "SELECT id FROM default_params WHERE user_id = ?"
        existing_params = self.db.fetchone(query_check, (params_data['user_id'],))

        if existing_params:
            query_update = """
                UPDATE default_params SET
                    period = ?, game_type = ?, tournament_type = ?, limit = ?
                WHERE user_id = ?
            """
            self.db.execute(query_update, (
                params_data['period'], params_data['game_type'],
                params_data['tournament_type'], params_data['limit'], params_data['user_id']
            ))
        else:
            query_insert = """
                INSERT INTO default_params (user_id, period, game_type, tournament_type, limit)
                VALUES (?, ?, ?, ?, ?)
            """
            self.db.execute(query_insert, (
                params_data['user_id'], params_data['period'],
                params_data['game_type'], params_data['tournament_type'], params_data['limit']
            ))

    def import_data(self, data: Dict[str, Any]):
        """
        Импортирует данные из сложного словаря в базу данных,
        обновляя существующие записи или добавляя новые.
        """
        # Обработка данных пользователя
        user_data = data['serverData']['user']
        self.insert_or_update_user({
            'id': int(user_data['id']),
            'club_id': int(user_data['club_id']),
            'login': user_data['login'],
            'first_name': user_data['first_name'],
            'last_name': user_data['last_name'],
            'date_registration': user_data['date_registration'],
            'icon_type': user_data['icon_type'],
            'icon': user_data['icon'],
            'gcoin': int(user_data['gcoin']),
            'elo': float(user_data['elo']),
            'vk_id': user_data['vk_id'],
            'referee_license': bool(int(user_data['referee_license'])),
            'is_paid': bool(int(user_data['is_paid'])),
            'is_can_comment': bool(int(user_data['is_can_comment'])),
            'since': user_data['since'],
            'avatar_link': user_data['avatar_link'],
            'average_elo': float(data['serverData'].get('averageElo', 0))
        })

        # Обработка статистики пользователя
        stats_data = data['serverData']['stats']
        win_rate = stats_data['win_rate']
        self.insert_or_update_stat(
            int(user_data['id']),
            {
                'mafia': win_rate.get('mafia', {}),
                'red': win_rate.get('red', {}),
                'don': win_rate.get('don', {}),
                'sheriff': win_rate.get('sheriff', {}),
                'win_strike': stats_data.get('win_strike', {}),
                'games_stats': stats_data.get('games_stats', {})
            }
        )

        # Обработка истории турниров
        tournament_data = data['serverData']['history']
        self.insert_or_update_tournament(int(user_data['id']), {
            'id': int(tournament_data['id']),
            'title': tournament_data['title'],
            'date_start': tournament_data['date_start'],
            'date_end': tournament_data['date_end'],
            'country_translate': tournament_data['country_translate'],
            'city_translate': tournament_data['city_translate'],
            'place': int(tournament_data['place']),
            'gg': float(tournament_data['gg']),
            'elo': int(tournament_data['elo'])
        })

        # Обработка игр в турнирах (если такие данные есть)
        if 'games' in tournament_data:
            tournament_games = tournament_data['games']
            self.insert_or_update_tournament_game({
                'tournament_id': int(tournament_data['id']),
                'game_num': int(tournament_games['game_num']),
                'role': tournament_games['role'],
                'place': int(tournament_games['place']),
                'win': tournament_games['win'],
                'win_translate': tournament_games['win_translate'],
                'elo_change': int(tournament_games['elo'])
            })

        # Обработка истории рейтинга (elo_history)
        if 'chart' in data['serverData']:
            chart_data = data['serverData']['chart']
            elo_data = chart_data.get('elo', {})
            if elo_data:
                self.insert_or_update_elo_history({
                    'user_id': int(user_data['id']),
                    'tournament_id': elo_data['id'],
                    'date': elo_data['x'],
                    'elo': float(elo_data['y']),
                    'elo_delta': float(chart_data.get('elo_delta', {}).get('y', 0))
                })

        # Обработка параметров по умолчанию (default_params)
        if 'defaultParams' in data['serverData']:
            default_params = data['serverData']['defaultParams']
            self.insert_or_update_default_params({
                'user_id': int(user_data['id']),
                'period': default_params['period'],
                'game_type': default_params['gameType'],
                'tournament_type': default_params['tournamentType'],
                'limit': int(default_params['limit'])
            })
