from scraper.services.gomafia_scraper import PlayerScraper

if __name__ == "__main__":
    player_id = 6146  # Пример ID игрока
    scraper = PlayerScraper(player_id)
    scraper.get_player_tournaments()
    userinfo, history_of_tournaments, history_of_games = scraper.extract_data()
    print(userinfo)
    print(history_of_games[0])
    print(history_of_tournaments[0])