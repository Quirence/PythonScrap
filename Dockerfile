# Используем базовый образ Python 3.10
FROM python:3.10-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект в контейнер
COPY ./ ./

# Устанавливаем переменную среды, чтобы Python не буферизовал вывод
ENV PYTHONUNBUFFERED 1

# Команда по умолчанию: запуск Django-сервера
WORKDIR /app/pythonscrap
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
