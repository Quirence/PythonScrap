import requests
from bs4 import BeautifulSoup
import json

url = 'https://zielinskiandrozen.ru/collection/duhi-10ml'

# Выполняем GET-запрос к сайту
response = requests.get(url)

# Проверяем статус ответа
if response.status_code == 200:
    # Парсим HTML-страницу с помощью BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    output_file = "gomafia_page.html"
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(response.text)
    print(f"HTML-страница успешно сохранена в файл: {output_file}")