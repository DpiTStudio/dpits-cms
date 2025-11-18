"""
Настройки Django для проекта mysite.

Сгенерировано с помощью 'django-admin startproject' используя Django 5.2.6.

Для получения дополнительной информации об этом файле см.
https://docs.djangoproject.com/en/5.2/topics/settings/

Для полного списка настроек и их значений см.
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

import os
from pathlib import Path

# =============================================================================
# БАЗОВЫЕ ПУТИ ПРОЕКТА
# =============================================================================

# Базовая директория проекта (корневая папка проекта)
BASE_DIR = Path(__file__).resolve().parent.parent

# =============================================================================
# НАСТРОЙКИ БЕЗОПАСНОСТИ
# =============================================================================

# СЕКРЕТНЫЙ КЛЮЧ: Никогда не используйте этот ключ в продакшене!
SECRET_KEY = "django-insecure-gg&b-34chy82xwd424vn41_=i=nr$2mrxm5_-xj(ev6ed#h+_="

# РЕЖИМ ОТЛАДКИ: В продакшене должно быть False!
DEBUG = True

# РАЗРЕШЕННЫЕ ХОСТЫ: Список доменов/хостов, которые может обслуживать Django
ALLOWED_HOSTS = [
    "*",  # Разрешает все хосты (только для разработки!)
    "www.dpits-cms.ru",
    "dpits-cms.ru",
    "localhost",
    "127.0.0.1",
]

# =============================================================================
# ОПРЕДЕЛЕНИЕ ПРИЛОЖЕНИЙ
# =============================================================================

INSTALLED_APPS = [
    # Сторонние приложения (должны быть выше встроенных)
    "jazzmin",  # Улучшенная админ-панель
    "django_ckeditor_5",  # Расширенный текстовый редактор
    "django_cleanup",  # Автоматическое удаление неиспользуемых файлов
    # Встроенные приложения Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Пользовательские приложения проекта
    "main.apps.MainConfig",  # Главное приложение
    "news.apps.NewsConfig",  # Новости
    "portfolio.apps.PortfolioConfig",  # Портфолио
    "reviews.apps.ReviewsConfig",  # Отзывы
    "accounts.apps.AccountsConfig",  # Аккаунты пользователей
]

# =============================================================================
# ПРОМЕЖУТОЧНОЕ ПО (MIDDLEWARE)
# =============================================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",  # Безопасность
    "django.contrib.sessions.middleware.SessionMiddleware",  # Сессии
    "django.middleware.common.CommonMiddleware",  # Общие функции
    "django.middleware.csrf.CsrfViewMiddleware",  # Защита CSRF
    "django.contrib.auth.middleware.AuthenticationMiddleware",  # Аутентификация
    "django.contrib.messages.middleware.MessageMiddleware",  # Сообщения
    "django.middleware.clickjacking.XFrameOptionsMiddleware",  # Защита от кликджекинга
]

# =============================================================================
# НАСТРОЙКИ URL И ШАБЛОНОВ
# =============================================================================

# Корневая конфигурация URL
ROOT_URLCONF = "mysite.urls"

# Настройки шаблонов
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,  # Поиск шаблонов в папках templates приложений
        "OPTIONS": {
            "context_processors": [
                # Стандартные процессоры контекста Django
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # Пользовательские процессоры контекста
                "main.context_processors.site_settings",  # Настройки сайта
                "main.context_processors.menu_items",  # Пункты меню
                "news.context_processors.latest_news",  # Последние новости
            ],
        },
    },
]

# WSGI приложение для развертывания
WSGI_APPLICATION = "mysite.wsgi.application"

# =============================================================================
# НАСТРОЙКИ БАЗЫ ДАННЫХ
# =============================================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",  # Движок базы данных
        "NAME": BASE_DIR / "db.sqlite3",  # Путь к файлу базы данных
    }
}

# =============================================================================
# ВАЛИДАЦИЯ ПАРОЛЕЙ
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# =============================================================================
# МЕЖДУНАРОДНЫЕ НАСТРОЙКИ (I18N/L10N)
# =============================================================================

LANGUAGE_CODE = "ru"  # Язык по умолчанию - русский
TIME_ZONE = "Europe/Moscow"  # Часовой пояс - Москва
USE_I18N = True  # Включение интернационализации
USE_TZ = True  # Использование часовых поясов

# =============================================================================
# НАСТРОЙКИ АУТЕНТИФИКАЦИИ И СЕССИЙ
# =============================================================================

# URL перенаправления после входа/выхода
LOGIN_REDIRECT_URL = "accounts:profile"
LOGOUT_REDIRECT_URL = "main:index"
LOGIN_URL = "accounts:login"  # URL для входа

# Хранилище сообщений (использует сессии)
MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

# =============================================================================
# СТАТИЧЕСКИЕ ФАЙЛЫ И МЕДИА
# =============================================================================

# Настройки статических файлов (CSS, JavaScript, изображения)
STATIC_URL = "/static/"  # URL префикс для статических файлов
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")  # Директория для collectstatic
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),  # Дополнительные директории со статикой
]

# Настройки медиа файлов (загружаемые пользователями)
MEDIA_URL = "/media/"  # URL префикс для медиа файлов
MEDIA_ROOT = os.path.join(BASE_DIR, "media")  # Директория для хранения медиа

# =============================================================================
# ПРОЧИЕ НАСТРОЙКИ DJANGO
# =============================================================================

# Тип поля первичного ключа по умолчанию
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =============================================================================
# НАСТРОЙКИ JAZZMIN (УЛУЧШЕННАЯ АДМИН-ПАНЕЛЬ)
# =============================================================================

JAZZMIN_SETTINGS = {
    # === ОСНОВНЫЕ НАСТРОЙКИ САЙТА ===
    "site_title": "Админ панель",  # Заголовок вкладки браузера
    "site_header": "Админ панель",  # Заголовок в админ-панели
    "site_brand": "Админ панель",  # Бренд в шапке
    "welcome_sign": "Добро пожаловать в админ панель",  # Приветственное сообщение
    # === НАСТРОЙКИ ЛОГОТИПА И ИКОНОК ===
    "site_logo": "images/logo.png",  # Логотип в шапке
    "site_icon": "images/logo.png",  # Иконка сайта
    "site_logo_classes": "img-circle",  # CSS классы для логотипа
    "login_logo": "images/logo.png",  # Логотип на странице входа
    "login_logo_size": "200px",  # Размер логотипа на странице входа
    # === ФУНКЦИОНАЛЬНОСТЬ ===
    "show_ui_builder": False,  # Отключить UI builder для продакшена
    "navigation_expanded": True,  # Развернутая навигация по умолчанию
    "hide_apps": [],  # Приложения для скрытия
    "hide_models": [],  # Модели для скрытия
    # === НАСТРОЙКИ МЕНЮ С УЛУЧШЕННЫМИ ИКОНКАМИ ===
    "menu": [
        {"app": "main", "label": "Главная", "icon": "fas fa-home"},
        {"app": "news", "label": "Новости", "icon": "fas fa-newspaper"},
        {"app": "portfolio", "label": "Портфолио", "icon": "fas fa-briefcase"},
        {"app": "reviews", "label": "Отзывы", "icon": "fas fa-star"},
        {"app": "accounts", "label": "Аккаунты", "icon": "fas fa-users"},
        {
            "app": "auth",
            "label": "Аутентификация",
            "icon": "fas fa-user-shield",
            "models": [
                {"name": "user", "label": "Пользователи", "icon": "fas fa-user"},
                {"name": "group", "label": "Группы", "icon": "fas fa-users-cog"},
            ],
        },
        {"app": "sites", "label": "Сайты", "icon": "fas fa-globe"},
    ],
    # === НАСТРОЙКИ СПИСКОВ ИЗМЕНЕНИЙ ===
    "changelist": {
        "show_delete_link": True,  # Показывать ссылку удаления
        "show_full_result_count": False,  # Не показывать полное количество результатов
    },
    # === ВНЕШНИЙ ВИД И ТЕМЫ ===
    "ui": {
        "theme": "darkly",  # Темная тема по умолчанию
        "dark_mode_theme": "darkly",  # Темная тема для темного режима
    },
    # === ДОПОЛНИТЕЛЬНЫЕ УЛУЧШЕНИЯ ===
    # "search_model": ["auth.User", "main.Profile"],  # Модели для поиска в хедере
    "topmenu_links": [
        {
            "name": "На сайт",
            "url": "/",
            "new_tab": True,  # Открывать в новой вкладке
            "icon": "fas fa-external-link-alt",
        },
        # {
        #     "name": "Документация",
        #     "url": "https://docs.djangoproject.com/",
        #     "new_tab": True,
        #     "icon": "fas fa-book",
        # },
    ],
    "show_sidebar": True,  # Показывать боковую панель
    "order_with_respect_to": [  # Порядок приложений в меню
        "main",
        "news",
        "portfolio",
        "reviews",
        "accounts",
        "auth",
    ],
    # === ИКОНКИ ДЕЙСТВИЙ ===
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        # "main.Profile": "fas fa-address-card",
        "news.News": "fas fa-newspaper",
        "portfolio.Project": "fas fa-briefcase",
        "reviews.Review": "fas fa-star",
        "accounts.User": "fas fa-user-circle",
    },
}

# =============================================================================
# НАСТРОЙКИ ВНЕШНЕГО ВИДА JAZZMIN
# =============================================================================

JAZZMIN_UI_TWEAKS = {
    # === НАСТРОЙКИ НАВИГАЦИИ ===
    "navbar": "navbar-white navbar-light",  # Светлая навигационная панель
    "navbar_fixed": True,  # Фиксированная навигационная панель
    "no_navbar_border": False,  # Граница навигационной панели
    # === НАСТРОЙКИ БОКОВОЙ ПАНЕЛИ ===
    "sidebar": "sidebar-dark-primary",  # Темная боковая панель
    "sidebar_fixed": True,  # Фиксированная боковая панель
    "sidebar_nav_small_text": False,  # Размер текста в навигации
    "sidebar_nav_child_indent": True,  # Отступы дочерних элементов
    "sidebar_nav_compact_style": True,  # Компактный стиль
    "sidebar_nav_legacy_style": True,  # Устаревший стиль
    "sidebar_nav_flat_style": True,  # Плоский стиль
    # === НАСТРОЙКИ ТЕМЫ ===
    "theme": "default",  # Основная тема
    "dark_mode_theme": None,  # Темная тема (None для отключения)
    # === НАСТРОЙКИ КНОПОК ===
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
    # === ПРОЧИЕ НАСТРОЙКИ ===
    "actions_sticky_top": False,  # Закрепление действий вверху
    "brand_colour": False,  # Цвет бренда
    "accent": "accent-primary",  # Акцентный цвет
}

# =============================================================================
# НАСТРОЙКИ CKEDITOR 5 (РАСШИРЕННЫЙ ТЕКСТОВЫЙ РЕДАКТОР)
# =============================================================================

CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "heading",
            "|",
            "bold",
            "italic",
            "link",
            "bulletedList",
            "numberedList",
            "blockQuote",
            "imageUpload",
            "mediaEmbed",
            "insertTable",
            "undo",
            "redo",
        ],
    },
    "extends": {
        "blockToolbar": [
            "paragraph",
            "heading1",
            "heading2",
            "heading3",
            "|",
            "bulletedList",
            "numberedList",
            "|",
            "blockQuote",
            "imageUpload",
        ],
        "toolbar": [
            "heading",
            "|",
            "outdent",
            "indent",
            "|",
            "bold",
            "italic",
            "link",
            "underline",
            "strikethrough",
            "code",
            "subscript",
            "superscript",
            "highlight",
            "|",
            "codeBlock",
            "sourceEditing",
            "insertImage",
            "bulletedList",
            "numberedList",
            "todoList",
            "|",
            "blockQuote",
            "imageUpload",
            "|",
            "fontSize",
            "fontFamily",
            "fontColor",
            "fontBackgroundColor",
            "mediaEmbed",
            "removeFormat",
            "insertTable",
        ],
        "image": {
            "toolbar": [
                "imageTextAlternative",
                "|",
                "imageStyle:alignLeft",
                "imageStyle:alignRight",
                "imageStyle:alignCenter",
                "imageStyle:side",
                "|",
            ],
            "styles": ["full", "side", "alignLeft", "alignRight", "alignCenter"],
        },
        "table": {
            "contentToolbar": [
                "tableColumn",
                "tableRow",
                "mergeTableCells",
                "tableProperties",
                "tableCellProperties",
            ],
            "tableProperties": {
                "borderColors": [
                    {"color": "#ccc"},
                    {"color": "#999"},
                    {"color": "#666"},
                    {"color": "#333"},
                    {"color": "#000"},
                ],
                "backgroundColors": [
                    {"color": "#fff"},
                    {"color": "#f8f9fa"},
                    {"color": "#e9ecef"},
                    {"color": "#dee2e6"},
                    {"color": "#ced4da"},
                ],
            },
        },
        "heading": {
            "options": [
                {
                    "model": "paragraph",
                    "title": "Paragraph",
                    "class": "ck-heading_paragraph",
                },
                {
                    "model": "heading1",
                    "view": "h1",
                    "title": "Heading 1",
                    "class": "ck-heading_heading1",
                },
                {
                    "model": "heading2",
                    "view": "h2",
                    "title": "Heading 2",
                    "class": "ck-heading_heading2",
                },
                {
                    "model": "heading3",
                    "view": "h3",
                    "title": "Heading 3",
                    "class": "ck-heading_heading3",
                },
            ]
        },
    },
    "list": {
        "properties": {
            "styles": "true",
            "startIndex": "true",
            "reversed": "true",
        }
    },
}

# Дополнительные настройки CKEditor 5
CKEDITOR_5_ALLOW_ALL_TAGS = True  # Разрешить все HTML теги
CKEDITOR_5_FILE_UPLOAD_PERMISSIONS = 0o644  # Права для загружаемых файлов

# =============================================================================
# НАСТРОЙКИ КЕШИРОВАНИЯ (ОТКЛЮЧЕНО)
# =============================================================================

# Кеширование отключено для разработки
# CACHES = {
#     "default": {
#         "BACKEND": "django.core.cache.backends.dummy.DummyCache",  # Заглушка для кеша
#     }
# }

# Движок сессий без кеширования
SESSION_ENGINE = "django.contrib.sessions.backends.db"  # Использование БД для сессий

# =============================================================================
# НАСТРОЙКИ ЭЛЕКТРОННОЙ ПОЧТЫ (ЗАКОММЕНТИРОВАНЫ)
# =============================================================================

# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
# # Для разработки
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# # Для продакшена
# EMAIL_HOST = "smtp.yandex.ru"
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = "noreply@yourdomain.com"
# EMAIL_HOST_PASSWORD = "your_password"
# DEFAULT_FROM_EMAIL = "noreply@yourdomain.com"

# =============================================================================
# НАСТРОЙКИ ЛОГИРОВАНИЯ
# =============================================================================

# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,  # Не отключать существующие логгеры
#     "handlers": {
#         "file": {
#             "level": "INFO",  # Уровень логирования
#             "class": "logging.FileHandler",  # Обработчик - файл
#             "filename": os.path.join(BASE_DIR, "debug.log"),  # Файл лога
#         },
#     },
#     "loggers": {
#         "django": {
#             "handlers": ["file"],
#             "level": "INFO",  # Уровень для Django
#             "propagate": True,  # Распространение логов
#         },
#         "portfolio": {
#             "handlers": ["file"],
#             "level": "INFO",  # Уровень для приложения portfolio
#             "propagate": False,  # Не распространять логи
#         },
#     },
# }
