# Приложение `portfolio` — Портфолио и Заказы

Демонстрация выполненных работ, управление клиентами и система заказов с встроенным чатом. При публикации работы автоматически создаётся новость.

---

## 📁 Структура файлов

```
portfolio/
├── models.py           # Модели: Client, PortfolioCategory, PortfolioItem, Order, OrderMessage, PortfolioReview
├── views.py            # Представления
├── urls.py             # URL-маршруты
├── forms.py            # Формы
├── admin.py            # Конфигурация Django Admin
├── apps.py             # Конфигурация приложения
├── signals.py          # Django-сигналы
├── utils.py            # Вспомогательные функции (custom_upload_to)
├── migrations/         # Миграции базы данных
├── static/             # CSS, JS
└── templates/portfolio/  # HTML-шаблоны
```

---

## 📦 Модели (`models.py`)

### `Client` — Клиент/Заказчик

| Поле | Тип | Описание |
|------|-----|----------|
| `user` | OneToOneField→User | Связь с пользователем |
| `company` | CharField(200) | Название компании |
| `phone` | CharField(20) | Телефон |
| `website` | URLField | Веб-сайт компании |
| `description` | CKEditor5Field | Описание клиента |
| `is_verified` | BooleanField | Подтверждён администратором |
| `created_at` | DateTimeField | Дата создания |

---

### `PortfolioCategory` — Категории портфолио

Наследует `HeroMixin`.

| Поле | Тип | Описание |
|------|-----|----------|
| `name` | CharField(100) | Название |
| `slug` | SlugField | Уникальный URL |
| `image` | ImageField | Изображение |
| `description` | CKEditor5Field | Описание |
| `seo_*` | CharField | SEO-поля |
| `order` | IntegerField | Порядок (больше = выше) |
| `is_active` | BooleanField | Активность |

- `save()` — автогенерация уникального slug
- `get_absolute_url()` → `/portfolio/category/<slug>/`
- `works_count()` — количество работ в категории

---

### `PortfolioItem` — Работа портфолио

Наследует `HeroMixin`.

**Статусы:**
| Значение | Описание |
|---------|----------|
| `draft` | Черновик (не виден на сайте) |
| `published` | Опубликовано |
| `archived` | В архиве |

| Поле | Тип | Описание |
|------|-----|----------|
| `title` | CharField(200) | Заголовок работы |
| `slug` | SlugField | Уникальный URL (автогенерация) |
| `category` | ForeignKey→PortfolioCategory | Категория (CASCADE) |
| `client` | ForeignKey→Client | Клиент (SET_NULL, необязательно) |
| `image` | ImageField | Главное изображение |
| `short_description` | TextField(300) | Краткое описание |
| `content` | CKEditor5Field | Полное описание |
| `technologies` | CharField(300) | Технологии (через запятую) |
| `project_date` | DateField | Дата выполнения |
| `project_url` | URLField | Ссылка на проект |
| `github_url` | URLField | Ссылка на GitHub |
| `status` | CharField | Статус публикации |
| `views` | PositiveIntegerField | Счётчик просмотров |
| `seo_*` | CharField | SEO-поля |

**Ключевые методы:**
- `save()` — автогенерация slug + **при статусе `published` вызывает `create_news_from_portfolio()`**
- `get_absolute_url()` → `/portfolio/<slug>/`
- `get_technologies_list()` — список технологий из строки через запятую
- `increment_views()` — увеличение счётчика просмотров
- `create_news_from_portfolio()` — автоматически создаёт новость в категории «Портфолио» (если не существует)
- `create_news_content()` — генерирует HTML-контент новости из данных работы

---

### `Order` — Заказ

**Статусы:** `new` (Новый), `in_progress` (В работе), `completed` (Завершён), `cancelled` (Отменён)

**Приоритеты:** `low` (Низкий), `medium` (Средний), `high` (Высокий), `urgent` (Срочный)

| Поле | Тип | Описание |
|------|-----|----------|
| `client` | ForeignKey→Client | Заказчик (CASCADE) |
| `title` | CharField(200) | Название проекта |
| `description` | TextField | Описание проекта |
| `budget` | DecimalField | Бюджет |
| `deadline` | DateField | Срок выполнения |
| `status` | CharField | Статус заказа |
| `priority` | CharField | Приоритет |
| `requirements_file` | FileField | Файл с требованиями |
| `additional_notes` | TextField | Дополнительные заметки |

**Свойства:**
- `is_overdue` → `True` если дедлайн прошёл
- `get_progress_percentage()` → процент выполнения по статусу (new=25%, in_progress=50%, completed=100%)

---

### `OrderMessage` — Сообщение в заказе

| Поле | Тип | Описание |
|------|-----|----------|
| `order` | ForeignKey→Order | Заказ. Обратная: `order.messages` |
| `user` | ForeignKey→User | Автор сообщения |
| `message` | TextField | Текст сообщения |
| `file` | FileField | Прикреплённый файл |
| `is_admin_message` | BooleanField | Автоопределяется: True если `user.is_staff` |

---

### `PortfolioReview` — Отзыв о работе

| Поле | Тип | Описание |
|------|-----|----------|
| `client` | ForeignKey→Client | Клиент-автор |
| `portfolio_item` | ForeignKey→PortfolioItem | Работа |
| `rating` | IntegerField | Рейтинг 1–5 |
| `title` | CharField(200) | Заголовок отзыва |
| `content` | TextField | Текст отзыва |
| `is_approved` | BooleanField | Одобрен администратором |

- Уникальность: один отзыв на пару (client, portfolio_item)
- `get_star_rating()` — HTML-разметка звёздного рейтинга

---

## 🌐 Представления (`views.py`)

| Функция/Класс | URL | Описание |
|---------------|-----|----------|
| `portfolio_list` | `/portfolio/` | Галерея опубликованных работ, фильтрация по категории |
| `portfolio_detail` | `/portfolio/<slug>/` | Детальная страница работы + счётчик просмотров |
| `portfolio_category` | `/portfolio/category/<slug>/` | Работы по категории |
| `order_create` | `/portfolio/order/create/` | Создание заказа (только клиенты) |
| `order_detail` | `/portfolio/order/<pk>/` | Просмотр заказа + чат |
| `client_profile` | `/portfolio/client/` | Профиль клиента |

---

## 🗺 URL-маршруты

Пространство имён: `portfolio`

| Имя | URL |
|-----|-----|
| `portfolio:list` | `/portfolio/` |
| `portfolio:detail` | `/portfolio/<slug>/` |
| `portfolio:category_list` | `/portfolio/category/<slug>/` |
| `portfolio:order_detail` | `/portfolio/order/<pk>/` |
| `portfolio:client_profile` | `/portfolio/client/` |

---

## 💡 Ключевые особенности

- **Автоновость:** при публикации `PortfolioItem` (`status = "published"`) автоматически создаётся новость в разделе «Портфолио» (один раз, при повторной публикации — игнорируется)
- **Чат внутри заказа:** модель `OrderMessage` поддерживает файловые вложения и различает сообщения клиента и администратора
- **Рейтинг:** HTML-звёзды генерируются методом `get_star_rating()` с font-awesome иконками
