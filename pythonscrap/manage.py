#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from scraper.db.database import *


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pythonscrap.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    # database = DatabaseManager()
    # for i in range(3000, 3500):
    #     database.add_player_from_id(i)
    # Раскомментировать для быстрого заполнения базы
    main()
