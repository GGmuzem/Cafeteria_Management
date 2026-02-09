FROM python:3.12-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код проекта
COPY . .

# Настройки для Python (чтобы вывод не буферизировался)
ENV PYTHONUNBUFFERED=1

# Запускаем Flask на порту 8080, доступном извне (0.0.0.0)
# Убедитесь, что FLASK_APP указывает на точку входа (например, src/app.py или src/main.py)
CMD ["python", "src/app.py"]
