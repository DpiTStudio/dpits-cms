# Конфигурация проекта (`mysite/`)

Папка `mysite/` содержит основные файлы настроек и маршрутизации для всего Django-проекта DPITS-CMS.

---

## 📁 Структура файлов

```
mysite/
├── settings.py         # Главный файл настроек Django
├── urls.py             # Корневой маршрутизатор URL
├── sitemaps.py         # XML-карта сайта для SEO
├── asgi.py             # ASGI-конфигурация (асинхронное развёртывание)
├── wsgi.py             # WSGI-конфигурация (синхронное развёртывание)
├── passenger_wsgi.py   # WSGI для хостинга с Passenger
└── __init__.py         # Инициализатор пакета Python
```

---

## ⚙️ Настройки (`settings.py`)

### Безопасность
| Параметр | Источник | Описание |
|---------|---------|----------|
| `SECRET_KEY` | `.env` | Секретный ключ Django |
| `DEBUG` | `.env` | Режим отладки (True/False) |
| `ALLOWED_HOSTS` | `.env` | Разрешённые хосты |

### Установленные приложения (`INSTALLED_APPS`)
```
django.contrib.admin        — Панель администратора
django.contrib.auth         — Аутентификация
django.contrib.contenttypes — Типы контента
django.contrib.sessions     — Сессии
django.contrib.messages     — Сообщения
django.contrib.staticfiles  — Статические файлы
django.contrib.sitemaps     — XML-карта сайта
jazzmin                     — Тема для Django Admin
django_ckeditor_5           — WYSIWYG-редактор
captcha                     — Капча
django_cleanup              — Автоочистка медиафайлов
main                        — Ядро сайта
news                        — Новости
services                    — Услуги
portfolio                   — Портфолио
reviews                     — Отзывы
accounts                    — Пользователи
feedback                    — Обратная связь
knowledge_base              — База знаний
```

### База данных
- **По умолчанию:** SQLite (`db.sqlite3`) для разработки
- **Продакшн:** настраивается через `DATABASE_URL` в `.env`

### Медиа и статика
| Параметр | Значение | Описание |
|---------|---------|----------|
| `MEDIA_URL` | `/media/` | URL для доступа к медиафайлам |
| `MEDIA_ROOT` | `BASE_DIR/media/` | Папка медиафайлов на диске |
| `STATIC_URL` | `/static/` | URL статических файлов |
| `STATIC_ROOT` | `BASE_DIR/staticfiles/` | Папка собранной статики |
| `STATICFILES_DIRS` | `BASE_DIR/static/` | Исходные статические файлы |

### Кэширование
- Используется Django cache framework
- Кэш меню навигации: 600 сек (10 мин)
- Кэш настроек сайта: 300 сек (5 мин)
- Кэш главной страницы: 900 сек (15 мин)

### Логирование
| Файл | Назначение |
|------|-----------|
| `logs/debug.log` | Все сообщения (DEBUG и выше) |
| `logs/error.log` | Только ошибки (ERROR и выше) |

Настроена ротация логов: ограничение по размеру файла и количеству резервных копий.

### Настройки Jazzmin (тема Django Admin)
- Тёмная Premium тема
- Кастомные иконки для каждой модели в боковом меню
- Брендирование: заголовок «DPITS CMS»

### CKEditor 5
- Пресет `extends` — полный набор инструментов (таблицы, код, изображения, ссылки)
- Загрузка изображений через `/ckeditor5/` маршруты

---

## 🗺 Корневые URL (`urls.py`)

Файл является точкой входа для всех HTTP-запросов.

### Подключённые приложения

| URL-путь | Приложение | Назначение |
|----------|-----------|------------|
| `/` | `main.urls` | Главная страница и общие маршруты |
| `/admin/` | Django Admin | Панель администрирования |
| `/news/` | `news.urls` | Раздел новостей |
| `/portfolio/` | `portfolio.urls` | Портфолио и заказы |
| `/services/` | `services.urls` | Каталог услуг |
| `/reviews/` | `reviews.urls` | Отзывы |
| `/accounts/` | `accounts.urls` | Аккаунты и тикеты |
| `/feedback/` | `feedback.urls` | Обратная связь |
| `/knowledge-base/` | `knowledge_base.urls` | База знаний |
| `/ckeditor5/` | `django_ckeditor_5` | Загрузка файлов редактора |
| `/captcha/` | `captcha` | Маршруты капчи |

### Системные маршруты

| URL | Назначение |
|-----|-----------|
| `/sitemap.xml` | XML-карта сайта для поисковых систем |
| `/robots.txt` | Инструкции для поисковых роботов |
| `/news/feed/` | RSS-лента всех новостей |
| `/news/feed/<slug>/` | RSS-лента новостей по категории |

### Кастомные обработчики ошибок

```python
handler404 = "main.views.custom_404_view"  # Страница «Не найдено»
handler500 = "main.views.custom_500_view"  # Страница «Ошибка сервера»
```

---

## 🗺 Карта сайта (`sitemaps.py`)

Формирует XML-карту сайта доступную по `/sitemap.xml` для поисковых систем (Google, Яндекс).

**Включает разделы:**
- Главная страница
- Динамические CMS-страницы (`Page`)
- Новости (`News`)
- Работы портфолио (`PortfolioItem`)
- Услуги (`Service`)

---

## 🚀 Файлы развёртывания

### `asgi.py`
ASGI-конфигурация для асинхронных серверов (Daphne, Uvicorn, Gunicorn с uvicorn worker).

### `wsgi.py`
WSGI-конфигурация для синхронных серверов (Gunicorn, uWSGI).

### `passenger_wsgi.py`
Специализированная WSGI-конфигурация для хостингов, использующих Phusion Passenger.
