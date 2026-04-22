#!/bin/bash

set -e

echo "=== Развёртывание Django-приложения ==="

echo "[1/3] Применение миграций базы данных..."
python manage.py migrate --noinput

echo "[2/3] Сбор статических файлов..."
python manage.py collectstatic --noinput 2>/dev/null || echo "Статические файлы не настроены, пропуск."

echo "[3/3] Запуск сервера на порту 5000..."
python manage.py runserver 0.0.0.0:5000
