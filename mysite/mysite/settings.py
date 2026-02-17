# ============================================================================================= #
# ФАЙЛ: SETTINGS.PY                                                                             #
# ОПИСАНИЕ:                                                                                     #
# Главный файл конфигурации проекта Django. Содержит все глобальные настройки, включая          #
# подключение базы данных, установленные приложения, параметры безопасности и настройки статики.#
#                                                                                               #
# НЮАНСЫ И ФУНКЦИОНАЛ:                                                                          #
# 1. Безопасность:                                                                              #
#    - Загрузка секретных ключей из .env (SECRET_KEY, DEBUG).                                   #
#    - Настройка ALLOWED_HOSTS.                                                                 #
# 2. Подключенные модули (INSTALLED_APPS):                                                      #
#    - Сторонние: jazzmin (админка), ckeditor (редактор), captcha, cleanup.                     #
#    - Внутренние: main, news, portfolio, services, reviews, accounts, feedback.                #
# 3. Шаблоны и Контекст:                                                                        #
#    - Подключение кастомных context_processors для глобальных данных (меню, настройки, SEO).   #
# 4. Интерфейс (UI):                                                                            #
#    - JAZZMIN_SETTINGS: Глубокая настройка внешнего вида админ-панели (меню, иконки, тема).    #
#    - CKEDITOR_5_CONFIGS: Конфигурация панелей инструментов для визуального редактора.         #
# 5. Инфраструктура:                                                                            #
#    - Настройка БД (SQLite).                                                                   #
#    - Логирование (LOGGING) с ротацией файлов и разделением по уровням (DEBUG, ERROR).         #
#    - Email бекенд (Console для разработки).                                                   #
# ============================================================================================= #
"""
Настройки для проекта mysite.

Сгенерировано с помощью старт-пакета.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# =============================================================================
# БАЗОВЫЕ ПУТИ ПРОЕКТА
# =============================================================================

# Базовая директория проекта (корневая папка проекта)
BASE_DIR = Path(__file__).resolve().parent.parent

# =============================================================================
# НАСТРОЙКИ БЕЗОПАСНОСТИ
# =============================================================================

# СЕКРЕТНЫЙ КЛЮЧ: Загружается из .env файла
SECRET_KEY = os.getenv("SECRET_KEY")

# РЕЖИМ ОТЛАДКИ: Загружается из .env файла (по умолчанию False)
DEBUG = os.getenv("DEBUG") == "True"

# РАЗРЕШЕННЫЕ ХОСТЫ: Список доменов/хостов, которые может обслуживать система
ALLOWED_HOSTS = [
    "*",  # Разрешает все хосты (только для разработки!)
    "dpits-cms.ru",
    # "www.dpits-cms.ru",
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
    "captcha",  # Капча для защиты от спама
    "django_extensions",  # Расширения Django (для runserver_plus с HTTPS)
    # Встроенные приложения системы
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",  # Добавлено: для работы с фильтрами дат (например, naturaltime)
    # Пользовательские приложения проекта
    "main.apps.MainConfig",  # Главное приложение
    "news.apps.NewsConfig",  # Новости
    "portfolio.apps.PortfolioConfig",  # Портфолио
    "services.apps.ServicesConfig",  # Услуги
    "reviews.apps.ReviewsConfig",  # Отзывы
    "accounts.apps.AccountsConfig",  # Аккаунты пользователей
    "feedback.apps.FeedbackConfig",  # Обратная связь
    "knowledge_base.apps.KnowledgeBaseConfig",  # База знаний
    # "files.apps.FilesConfig",  # Управление файлами
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
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,  # Поиск шаблонов в папках templates приложений
        "OPTIONS": {
            "context_processors": [
                # Стандартные процессоры контекста
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # Пользовательские процессоры контекста
                "main.context_processors.site_settings",  # Настройки сайта
                "main.context_processors.menu_items",  # Пункты меню
                "main.context_processors.dynamic_menus",  # Динамические меню
                "main.context_processors.sidebar_data",  # Данные сайдбара
                "main.context_processors.seo_context",  # Базовые SEO-данные
                "main.context_processors.admin_dashboard_stats",  # Статистика для админки
                "main.context_processors.statistics_banners",  # Статистические баннеры
                "main.context_processors.hero_overrides",  # Динамические баннеры разделов
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
STATIC_ROOT = BASE_DIR / "staticfiles"  # Директория для collectstatic
STATICFILES_DIRS = [
    BASE_DIR / "static",  # Дополнительные директории со статикой
]

# Настройки медиа файлов (загружаемые пользователями)
MEDIA_URL = "/media/"  # URL префикс для медиа файлов
MEDIA_ROOT = BASE_DIR / "media"  # Директория для хранения медиа

# =============================================================================
# ПРОЧИЕ НАСТРОЙКИ СИСТЕМЫ
# =============================================================================

# Тип поля первичного ключа по умолчанию
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Настройка разрешений для автоматического создания новостей
AUTO_NEWS_CREATION = {
    "enabled": True,
    "only_published": True,
    "category_slug": "portfolio",
    "create_for": ["PortfolioItem"],  # Модели, для которых создавать новости
}

# =============================================================================
# НАСТРОЙКИ JAZZMIN (УЛУЧШЕННАЯ АДМИН-ПАНЕЛЬ)
# =============================================================================

JAZZMIN_SETTINGS = {
    # === ОСНОВНЫЕ НАСТРОЙКИ САЙТА ===
    "site_title": "DPITS CMS Админ",
    "site_header": "DPITS CMS",
    "site_brand": "DPITS CMS",
    "welcome_sign": "Добро пожаловать в панель управления",
    "copyright": "DPITS CMS",
    "show_version": False,
    # === НАСТРОЙКИ ПОИСКА ===
    # "search_model": ["auth.User", "portfolio.PortfolioItem", "news.News"],
    # === НАСТРОЙКИ ЛОГОТИПА И ИКОНОК ===
    "site_logo": "images/logo.png",
    "site_logo_size": "100px",
    "login_logo": "images/logo.png",
    "login_logo_size": "100px",
    # === ФУНКЦИОНАЛЬНОСТЬ ===
    "show_ui_builder": False,
    "navigation_expanded": True,
    # === МЕНЮ (Top Menu) ===
    "topmenu_links": [
        {
            "name": "Публик",
            "url": "/",
            "new_tab": True,
            "icon": "fas fa-external-link-alt",
        },
        {
            "name": "Стат",
            "url": "/log-stats/",
            "new_tab": True,
            "icon": "fas fa-chart-line",
        },
        {
            "name": "Лог",
            "url": "/error-log/",
            "new_tab": True,
            "icon": "fas fa-bug",
        },
    ],
    # === БОКОВОЕ МЕНЮ (Side Menu) ===
    "show_sidebar": True,
    "show_sidebar_numbers": True,
    "order_with_respect_to": [
        "main",
        "news",
        "portfolio",
        "services",
        "reviews",
        "accounts",

        "feedback",
        "knowledge_base",
        "auth",
    ],
    # === ИКОНКИ МОДЕЛЕЙ (FontAwesome) ===
    "icons": {
        # AUTH
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user-shield",
        "auth.Group": "fas fa-users",
        # MAIN
        "main": "fas fa-cogs",
        "main.SiteSettings": "fas fa-sliders-h",
        "main.SEOData": "fab fa-google",
        "main.MenuItem": "fas fa-bars",
        "main.SidebarItem": "fas fa-list-ul",
        "main.LogStats": "fas fa-chart-bar",
        "main.ErrorLog": "fas fa-exclamation-triangle",
        # NEWS
        "news": "fas fa-newspaper",
        "news.Category": "fas fa-folder",
        "news.News": "fas fa-file-alt",
        # PORTFOLIO
        "portfolio": "fas fa-briefcase",
        "portfolio.Category": "fas fa-tags",
        "portfolio.PortfolioItem": "fas fa-paint-brush",
        "portfolio.Client": "fas fa-user-tie",
        "portfolio.PortfolioReview": "fas fa-quote-right",
        "portfolio.Order": "fas fa-shopping-cart",
        "portfolio.OrderMessage": "fas fa-comment-dollar",
        # REVIEWS
        "reviews": "fas fa-star",
        "reviews.Review": "fas fa-star-half-alt",
        # ACCOUNTS
        "accounts": "fas fa-id-card",
        "accounts.Profile": "fas fa-id-badge",
        # FEEDBACK
        "feedback": "fas fa-headset",
        "feedback.FeedbackMessage": "fas fa-envelope-open-text",
        "feedback.Ticket": "fas fa-ticket-alt",
        "feedback.TicketResponse": "fas fa-reply",
        # KNOWLEDGE BASE
        "knowledge_base": "fas fa-book",
        "knowledge_base.Category": "fas fa-bookmark",
        "knowledge_base.Article": "fas fa-file-alt",
        # SITES
        "sites.Site": "fas fa-globe",
    },
    # === СТРУКТУРА МЕНЮ ===
    "menu": [
        {
            "app": "main",
            "label": "Основные настройки",
            "icon": "fas fa-cogs",
            "models": [
                "main.SiteSettings",
                "main.SEOData",
                "main.LogStats",
                "main.ErrorLog",
            ],
        },
        {"app": "news", "label": "Новости", "icon": "fas fa-newspaper"},
        {"app": "portfolio", "label": "Портфолио", "icon": "fas fa-briefcase"},
        {"app": "services", "label": "Услуги", "icon": "fas fa-concierge-bell"},
        {"app": "reviews", "label": "Отзывы", "icon": "fas fa-star"},
        {"app": "accounts", "label": "Учетные записи", "icon": "fas fa-users"},
        {"app": "feedback", "label": "Обратная связь", "icon": "fas fa-envelope"},
        {"app": "knowledge_base", "label": "База знаний", "icon": "fas fa-book"},
        {"app": "auth", "label": "Администрирование", "icon": "fas fa-shield-alt"},
    ],
    # === ВНЕШНИЙ ВИД ===
    "ui": {
        "theme": "darkly",
        "dark_mode_theme": "darkly",
    },
    # === CUSTOM CSS & JS ===
    "custom_css": "css/admin_custom.css",
    "custom_js": "js/admin_font_size.js",
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
# НАСТРОЙКИ КЕШИРОВАНИЯ
# =============================================================================

# Кеширование для разработки (использует заглушку, не требует Redis)
# CACHES = {
#     "default": {
#         "BACKEND": "django.core.cache.backends.dummy.DummyCache",  # Заглушка для кеша
#     }
# }

# Движок сессий без кеширования
SESSION_ENGINE = "django.contrib.sessions.backends.db"  # Использование БД для сессий

# =============================================================================
# НАСТРОЙКИ ЭЛЕКТРОННОЙ ПОЧТЫ
# =============================================================================

# Для разработки: письма выводятся в консоль
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Для продакшена: раскомментируйте следующие строки и настройте SMTP
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_HOST = "smtp.yandex.ru"
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = "noreply@yourdomain.com"
# EMAIL_HOST_PASSWORD = "your_password"
# DEFAULT_FROM_EMAIL = "noreply@yourdomain.com"

# Email администратора для уведомлений (можно переопределить в SiteSettings)
# ADMIN_EMAIL = None  # Если None, будет использован email из SiteSettings или первого суперпользователя

# =============================================================================
# НАСТРОЙКИ ЛОГИРОВАНИЯ
# =============================================================================

# # Создаем папку для логов если её нет
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": (
                "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d "
                "%(funcName)s() | %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "%(asctime)s [%(levelname)s] %(message)s",
            "datefmt": "%H:%M:%S",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "debug.log",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "encoding": "utf-8",
            "formatter": "detailed",
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "error.log",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 3,
            "encoding": "utf-8",
            "formatter": "detailed",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file", "error_file", "console"],
            "level": "INFO",
            "propagate": True,
        },
        "django.server": {
            "handlers": ["console"],
            "level": "WARNING",  # Скрываем INFO сообщения о HTTPS (они будут как WARNING)
            "propagate": False,
        },
        "portfolio": {
            "handlers": ["file", "error_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "security": {
            "handlers": ["error_file"],
            "level": "WARNING",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}


# Настройки капчи для защиты от спама
CAPTCHA_CHALLENGE_FUNCT = (
    "captcha.helpers.random_char_challenge"  # Функция генерации капчи
)
CAPTCHA_LENGTH = 3  # Длина капчи (количество символов)
CAPTCHA_TIMEOUT = 10  # Время жизни капчи в минутах
CAPTCHA_NOISE_FUNCTIONS = (
    "captcha.helpers.noise_arcs",  # Добавление дуг для усложнения
    "captcha.helpers.noise_dots",  # Добавление точек для усложнения
)
CAPTCHA_FONT_SIZE = 40  # Размер шрифта капчи
CAPTCHA_IMAGE_SIZE = (120, 50)  # Размер изображения капчи (ширина, высота)
