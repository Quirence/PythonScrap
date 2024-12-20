# Используем полный образ Python
FROM python:3.10

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . /app

# Устанавливаем зависимости
RUN pip install --upgrade pip && pip install -r requirements.txt

# Открываем порт для Django
EXPOSE 8000

# Переходим в папку с manage.py перед запуском
WORKDIR /app/pythonscrap

# Команда для запуска Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
