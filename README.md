# DPITS-CMS (DpiTStudio CMS)

![Project Hero](file:///C:/Users/ADMIN/.gemini/antigravity-ide/brain/6e376d39-e879-4140-a44d-71990702b6eb/project_hero_image_1780751575202.png)

[![Django](https://img.shields.io/badge/Django-5.2.6-blue)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11%2B-brightgreen)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Proprietary-red)](#license)

## 📖 Оглавление
- [Введение](#введение)
- [Основные возможности](#основные-возможности)
- [Технологический стек](#технологический-стек)
- [Установка и запуск](#установка-и-запуск)
- [Развертывание в Production](#развёртывание-в-production)
- [Сервисные команды](#сервисные-команды)
- [Мониторинг и безопасность](#мониторинг-и-безопасность)
- [Участие в разработке](#участие-в-разработке)
- [Лицензия](#лицензия)

## Введение
Комплексная система управления контентом на базе Django, предоставляющая готовые решения для новостных порталов, корпоративных сайтов, портфолио, личных кабинетов и тикет‑системы.

## Основные возможности
- Динамическое управление контентом (CMS)
- Портфолио и CRM
- Полноценные аккаунты пользователей и поддержка
- Безопасная обратная связь и отзывы
- Продвинутая админ‑панель с Jazzmin и CKEditor 5
- Файловый менеджер и резервные копии
- Мониторинг и аналитика в реальном времени

## Технологический стек
- **Backend:** Python 3.11+, Django 5.2.6
- **Database:** SQLite (dev), PostgreSQL / MySQL (prod)
- **Frontend:** HTML5, CSS3 (Vanilla, CSS‑переменные), Vanilla JS
- **UI:** Jazzmin, CKEditor 5
- **Security:** django‑simple‑captcha, django‑cleanup, django‑extensions
- **Performance:** Django Caching (Redis/Memcached)

## Установка и запуск
<details><summary>Показать шаги</summary>

1. **Клонировать репозиторий**
   ```bash
   git clone <url>
   cd dpits-cms
   ```
2. **Создать виртуальное окружение**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   ```
3. **Установить зависимости**
   ```bash
   pip install --upgrade pip
   pip install -r mysite/requirements.txt
   ```
4. **Применить миграции**
   ```bash
   cd mysite
   python manage.py makemigrations
   python manage.py migrate
   ```
5. **Создать суперпользователя**
   ```bash
   python manage.py createsuperuser
   ```
6. **Запустить сервер**
   ```bash
   python manage.py runserver
   ```
   Сайт будет доступен по `http://127.0.0.1:8000/`.
</details>

## Развёртывание в Production
(см. оригинальный README для подробностей)

## Сервисные команды
- `python manage.py backup_site` – резервное копирование
- `python manage.py clear_cache` – сброс кэша

## Мониторинг и безопасность
- Логи в `mysite/logs/`
- Статистика через `/log-stats/`

## Участие в разработке
Создавайте Issue или Pull Request в репозитории.

## Лицензия
Проект покрыт внутренними лицензионными соглашениями компании **DpiTStudio**.
