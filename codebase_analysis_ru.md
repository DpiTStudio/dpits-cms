# Архитектурный и пофайловый анализ DPITS-CMS

Этот документ содержит подробный анализ веб-сайта на базе Django (DPITS-CMS) и детальное описание структуры проекта, каждого каталога, приложения и ключевых файлов на русском языке.

---

## 1. Общая структура проекта

В корневом каталоге `mysite/` находятся управляющие файлы проекта, конфигурационные файлы среды и основные модули Django.

### Корневые файлы
* **[manage.py](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/manage.py)**: Стандартный скрипт командной строки Django для управления проектом (запуск сервера разработки, создание миграций, выполнение консольных команд и т.д.).
* **[.env](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/.venv)**: Конфигурационный файл для хранения чувствительных переменных окружения (секретный ключ Django, настройки базы данных, параметры отладки, ключи API).
* **[.env.example](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/.env.example)**: Шаблон для файла `.env` с указанием необходимых переменных для настройки проекта на других машинах.
* **[.htaccess](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/.htaccess)**: Конфигурационный файл для веб-сервера Apache (используется при развертывании на некоторых хостингах для перенаправления запросов).
* **[requirements.txt](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/requirements.txt)**: Список внешних Python-зависимостей проекта с указанием точных версий (включая Django, ckeditor-5, django-cleanup, pillow, django-simple-captcha и др.).
* **[bundle_css.py](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/bundle_css.py)**: Вспомогательный скрипт на Python для автоматической сборки, минификации и склеивания всех CSS-файлов проекта в один оптимизированный файл `bundle.min.css`. Он парсит файл `css.html` и собирает стили в нужном порядке.
* **[run_dev.bat](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/run_dev.bat)**, **[runserver_https.bat](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/runserver_https.bat)**: Исполняемые файлы Windows для быстрого запуска локального сервера разработки (включая поддержку HTTPS).
* **[runserver_https.sh](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/runserver_https.sh)**: Скрипт Bash для запуска сервера через HTTPS на Linux/macOS системах.
* **[db.sqlite3](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/db.sqlite3)**: Локальная база данных SQLite, используемая на этапе разработки.

---

## 2. Главные конфигурационные директории

### Директория `mysite/mysite/`
Это основное конфигурационное ядро Django-проекта:
* **[settings.py](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/mysite/settings.py)**: Главный конфигурационный файл Django. Определяет настройки безопасности, подключенные приложения, настройки сессий, шаблонов, медиа- и статических файлов, параметры кэширования и логирования.
* **[urls.py](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/mysite/urls.py)**: Главный диспетчер URL-адресов. Маршрутизирует входящие HTTP-запросы к соответствующим приложениям (main, accounts, news, services, portfolio, reviews, feedback, captcha и т.д.).
* **[wsgi.py](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/mysite/wsgi.py)** и **[asgi.py](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/mysite/asgi.py)**: Входные точки для WSGI и ASGI-совместимых веб-серверов для развертывания проекта в продакшене.
* **[passenger_wsgi.py](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/mysite/passenger_wsgi.py)**: Конфигурационный файл для интеграции с веб-серверами на базе хостинга cPanel/CloudLinux (Passenger).
* **[sitemaps.py](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/mysite/sitemaps.py)**: Генерирует XML-карту сайта (Sitemap) для поисковых систем (SEO), индексируя статические страницы, новости, категории и портфолио.

---

## 3. Детальный разбор Django-приложений

Проект разделен на 8 функциональных приложений. Каждое приложение построено по стандартной архитектуре MVT (Model-View-Template).

### 3.1. Приложение `main` (Основное ядро сайта)
Отвечает за базовые страницы (Главная, О нас, Контакты), обработку ошибок, бэкапы, системные логи и отображение информации о сервере.
* **[models.py](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/main/models.py)**: Содержит модели для статических страниц (`Page`), настроек сайта (`SiteSettings`), системных логов, баннеров статистики, текстовых блоков и хлебных крошек.
* **[views.py](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/main/views.py)**: Обрабатывает рендеринг главной страницы, контактов, страницы поиска, а также административные представления для управления бэкапами базы данных и логами сервера.
* **[admin.py](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/main/admin.py)** и **[admin_files.py](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/main/admin_files.py)**: Кастомизация административной панели Django для управления структурой страниц, медиа-файлами и интеграции визуального редактора CKEditor.
* **[backup_utils.py](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/main/backup_utils.py)**: Модуль для создания, удаления и восстановления резервных копий базы данных SQLite.
* **[log_utils.py](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/main/log_utils.py)**: Парсинг, фильтрация и анализ системных логов Django для их вывода в панель мониторинга.

### 3.2. Приложение `accounts` (Пользователи и безопасность)
Обеспечивает авторизацию, регистрацию, личные кабинеты, тикет-систему (техподдержку) и двухфакторную аутентификацию (2FA).
* **[models.py](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/accounts/models.py)**: Содержит расширенную модель пользователя `Profile`, модель тикетов техподдержки `Ticket` и сообщений к ним `TicketMessage`.
* **[views.py](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/accounts/views.py)**: Реализует регистрацию, логин, логаут, редактирование профиля, отправку тикетов и интерфейс переписки.
* **[two_factor.py](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/accounts/two_factor.py)**: Логика генерации и проверки TOTP-кодов для двухфакторной аутентификации через приложения (Google Authenticator и др.).

### 3.3. Приложение `services` (Услуги и корзина заказа)
Управляет списком услуг и процессом их заказа через интерактивную корзину на AJAX.
* **[models.py](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/services/models.py)**: Модели для категорий услуг (`ServiceCategory`), самих услуг (`Service`), элементов корзины и заказов (`Order`).
* **[cart.py](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/services/cart.py)**: Класс управления корзиной в рамках пользовательской сессии (добавление услуг, удаление, расчет стоимости).
* **[cart_views.py](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/services/cart_views.py)**: AJAX-представления для добавления/удаления услуг из корзины без перезагрузки страницы.

### 3.4. Приложение `news` (Публикации и Лента событий)
Новостной блог с возможностью группировки по категориям, комментирования и формирования RSS-ленты.
* **[models.py](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/news/models.py)**: Модели для новостей (`News`), категорий (`Category`) и комментариев (`Comment`).
* **[views.py](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/news/views.py)**: Рендеринг списка новостей с пагинацией, фильтрацией по категориям, детального просмотра статьи и обработки добавления комментариев.

### 3.5. Приложение `portfolio` (Проекты и кейсы)
Служит для демонстрации выполненных работ.
* **[models.py](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/portfolio/models.py)**: Модели проектов (`Project`), скриншотов/галереи проектов (`ProjectImage`), технологий (`Technology`) и заказов на разработку.
* **[views.py](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/portfolio/views.py)**: Выводит список проектов с фильтрацией по категориям и детальную страницу каждого кейса.

### 3.6. Приложение `reviews` (Отзывы)
Обработка и отображение отзывов клиентов.
* **[models.py](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/reviews/models.py)**: Модель отзыва (`Review`) с полями автора, рейтинга (звезды), текста и статуса модерации.

### 3.7. Приложение `feedback` (Обратная связь)
Модуль для отправки контактных форм.
* **[models.py](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/feedback/models.py)**: Модель обращений `Feedback` для фиксации вопросов пользователей в базе данных.

### 3.8. Приложение `knowledge_base` (База знаний)
Хранение и отображение обучающих и информационных статей.
* **[models.py](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/knowledge_base/models.py)**: Модели разделов и статей базы знаний.

---

## 4. Глобальные шаблоны и структура страниц

Главные файлы верстки лежат в каталоге `templates/`:
* **[_base.html](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/templates/_base.html)**: Каркас сайта. Содержит мета-теги, подключение Bootstrap, Google Fonts, Font Awesome, глобального CSS-бандла и скриптов. Описывает общую сетку: Header -> Main Content (с Sidebar в правой колонке) -> Footer.
* **Директория [layout/](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/templates/layout/)**:
  * `header.html`, `header_menu.html`: Шапка сайта с логотипом, навигацией и кнопками авторизации.
  * `footer.html`: Подвал сайта с контактной информацией и быстрыми ссылками.
  * `hero.html`: Адаптивный главный баннер (Hero-секция) страниц.
  * `sidebar.html`: Боковая панель для отображения виджетов (лента событий, форма обратной связи).
  * `css.html`: Список подключаемых CSS-файлов (используется сборщиком бандла).
  * `js.html`: Подключение внешних библиотек и инициализация кастомных JS-скриптов.

---

## 5. Файлы JavaScript (`static/js/`)

* **[main.js](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/static/js/main.js)**: UX-улучшения. Инициализация Ripple-эффекта на кнопках, скрытие мобильного меню при кликах, анимация отправки форм (добавление лоадеров на кнопки), инициализация тост-уведомлений.
* **[script.js](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/static/js/script.js)**: Базовый функционал. Инициализация стандартных подсказок (Bootstrap tooltips), валидация форм, превью загружаемых картинок в реальном времени, подсчет символов в текстовых полях. Содержит дублирующиеся обработчики плавного скролла по якорям.
* **[lazy-loading.js](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/static/js/lazy-loading.js)**: Реализация отложенной (ленивой) загрузки изображений на базе Intersection Observer для повышения производительности загрузки страниц.
* **[mobile-enhancements.js](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/static/js/mobile-enhancements.js)**: Скрипт для обработки свайп-жестов (открытие/закрытие бокового меню свайпами влево/вправо) и адаптации полей ввода на смартфонах.
* **[reading-progress.js](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/static/js/reading-progress.js)**: Индикатор прогресса чтения страницы (полоса в верхней части экрана, заполняющаяся по мере скроллинга страницы вниз).
* **[search.js](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/static/js/search.js)**: Реализует «живой» AJAX-поиск с автодополнением по мере ввода текста пользователем.
* **[cart.js](file:///b:/PYTHON/PROJECTS/dpits-cms/mysite/static/js/cart.js)**: Логика взаимодействия с корзиной услуг по AJAX. Добавление, удаление, пересчет сумм и обновление UI сайдбара.

---

## 6. Директории CSS-стилей (`static/css/`)

Стили структурированы по назначению и собираются в один файл `bundle.min.css`:
* `00_variables/`: Переменные CSS (палитра цветов, размеры шрифтов, отступы).
* `01_base/`: Сброс стандартных стилей браузеров, базовая типографика.
* `02_layout/`: Grid/Flex-разметка шапки, подвала и общей сетки страниц.
* `03_components/`: Карточки, кнопки, формы, сайдбар, пагинация.
* `04_sections/`: Разметка секций контента и отдельных типов страниц.
* `05_news/`, `06_portfolio/`: Стили для списков и детальных страниц публикаций и проектов.
* `07_effects/`:
  * `animations.css`: Keyframes для различных анимаций (пульсация, вращение, встряхивание).
  * `ui-enhancements.css`: Дополнительные эффекты микроинтеракций, скроллбар, кастомные тултипы.
* `99_premium/`:
  * `premium-enhancements.css`: Эффекты матового стекла (glassmorphism), неоновое свечение, переливы.
  * `visual-upgrade-2026.css`: Финальный слой премиум-стилизации (Scroll Reveal, Canvas-анимация частиц, Tilt-эффекты карт).

---

## 7. Проблемные зоны (потребность в оптимизации)

На основе анализа выявлены следующие недостатки:
1. **Перенасыщенность эффектами (Scroll Reveal)**:
   * Элементы с классом `.reveal-on-scroll` имеют `opacity: 0` и сдвигаются с помощью `translateY(40px)`. Если JS выполняется с задержкой или Intersection Observer не успевает срабатывать, контент остается скрытым или появляется рывками.
2. **Конфликты скролла (Scroll Hijacking)**:
   * В `script.js` присутствуют сразу два обработчика клика на ссылки с якорями `#` для плавной прокрутки. Это вызывает конфликты при клике и дерганье страницы.
   * `scroll-behavior: smooth` в сочетании с JS-скроллом перегружает поток рендеринга и создает ощущение лагов.
3. **Canvas-анимации частиц и Tilt-эффекты на карточках**:
   * Хотя они отключены в инициализации в некоторых файлах, неиспользуемые стили и скрипты все равно загружаются в браузер, создавая дополнительный вес.
