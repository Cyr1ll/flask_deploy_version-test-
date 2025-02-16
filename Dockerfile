# Используем официальный Python 3.13 slim-образ
FROM python:3.13-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

# Запускаем приложение 
CMD ["python","app.py"]
