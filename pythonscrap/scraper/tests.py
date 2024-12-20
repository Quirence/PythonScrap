from django.test import TestCase
from db.database import *
if __name__ == "__main__":
    database = DatabaseManager()
    for i in range(500, 1000):
        database.add_player_from_id(i)
# Create your tests her.
