@echo off
REM Скрипт для запуска Django сервера на порту 6678
REM Проверка и установка зависимостей (исправляет ошибку с captcha)

cd /d "%~dp0"

echo Проверка установленных пакетов...
pip install -r requirements.txt

echo.
echo Запуск сервера на http://127.0.0.1:6678/
python manage.py runserver 6678
