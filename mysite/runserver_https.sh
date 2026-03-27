#!/bin/bash
# Скрипт для запуска Django сервера с поддержкой HTTPS на порту 6678
cd "$(dirname "$0")"
echo "Активация виртуального окружения..."
source "../.venv/Scripts/activate"

python manage.py runserver_plus --cert-file cert.crt --key-file cert.key 127.0.0.1:6678
