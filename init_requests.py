import requests
from bs4 import BeautifulSoup
import json

url = 'https://gomafia.pro/stats/6146?tab=history'

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
    # Находим нужный тег <script>
    script_tag = soup.find('script', id='__NEXT_DATA__')

    if script_tag:
        # Извлекаем текст из тега
        json_data = script_tag.string

        # Преобразуем строку JSON в словарь Python
        data = json.loads(json_data)

        # Теперь вы можете работать с данными
        user_info = data['props']['pageProps']['serverData']['user']
        print(user_info)
    else:
        print("Тег <script> с id='NEXT_DATA' не найден.")
else:
    print(f"Ошибка при запросе: {response.status_code}")
