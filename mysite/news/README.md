# Приложение `news` — Новости

Система управления новостями: публикация, категории, теги, RSS-ленты, поиск, пагинация, счётчик просмотров.

---

## 📁 Структура файлов

```
news/
├── models.py           # Модели: NewsTag, NewsCategory, News
├── views.py            # Представления
├── urls.py             # URL-маршруты
├── admin.py            # Конфигурация Django Admin
├── apps.py             # Конфигурация приложения
├── feeds.py            # RSS-ленты новостей
├── context_processors.py  # Контекст-процессор
├── utils.py            # Кэширование категорий и сайдбара
├── migrations/         # Миграции базы данных
├── static/             # CSS, JS
└── templates/news/     # HTML-шаблоны
```

---

## 📦 Модели (`models.py`)

### `NewsTag` — Теги

| Поле | Тип | Описание |
|------|-----|----------|
| `name` | CharField(50) | Название тега, уникальное |
| `slug` | SlugField(50) | URL-идентификатор, автогенерация |

- `save()` — автогенерация `slug` из `name`
- `get_absolute_url()` → `/news/tag/<slug>/`

---

### `NewsCategory` — Категории

Наследует `HeroMixin` (поля баннера).

| Поле | Тип | Описание |
|------|-----|----------|
| `name` | CharField(100) | Название категории |
| `slug` | SlugField | Уникальный URL |
| `image` | ImageField | Изображение категории |
| `description` | CKEditor5Field | Описание (WYSIWYG) |
| `seo_title/keywords/description` | CharField | SEO-поля |
| `show_in_menu` | BooleanField | Показывать в меню |
| `order` | IntegerField | Порядок сортировки |
| `is_active` | BooleanField | Активность |
| `views` | PositiveIntegerField | Счётчик просмотров |

- `save()` — автогенерация уникального slug с суффиксом (`cat-1`, `cat-2`)
- `get_absolute_url()` → `/news/category/<slug>/`
- Сортировка: `["order", "name"]`

---

### `News` — Новость

Наследует `HeroMixin`.

| Поле | Тип | Описание |
|------|-----|----------|
| `title` | CharField(200) | Заголовок |
| `slug` | SlugField | Уникальный URL |
| `category` | ForeignKey→NewsCategory | Категория (PROTECT) |
| `image` | ImageField | Изображение (`news/`) |
| `is_active` | BooleanField | Опубликована |
| `short_description` | CKEditor5Field | Анонс (для списков) |
| `content` | CKEditor5Field | Полное содержимое |
| `tags` | ManyToManyField→NewsTag | Теги |
| `views` | PositiveIntegerField | Счётчик просмотров |
| `created_at` | DateTimeField | Дата создания (auto) |
| `updated_at` | DateTimeField | Дата обновления (auto) |
| `seo_*` | CharField | SEO-поля |

- `save()` — автогенерация уникального slug
- `get_absolute_url()` → `/news/<slug>/`
- `increment_views()` — **атомарный** счётчик через `F("views") + 1` (защита от race condition)
- Сортировка: `["-created_at"]`

---

## 🌐 Представления (`views.py`)

| Функция | URL | Шаблон | Описание |
|---------|-----|--------|----------|
| `news_list` | `/news/` | `news/list.html` | Все новости. GET: `q`, `sort`, `category`, `page`. Пагинация 20/стр |
| `news_detail` | `/news/<slug>/` | `news/detail.html` | Статья. Счётчик просмотров, похожие новости, новости за ту же дату |
| `news_by_category` | `/news/category/<slug>/` | `news/category.html` | Новости категории. GET: `q`, `sort`, `page` |
| `news_search` | `/news/search/` | `news/search.html` | Поиск по title, short_description, content |
| `news_by_tag` | `/news/tag/<slug>/` | `news/list.html` | Новости по тегу |

---

## 📡 RSS-ленты (`feeds.py`)

| Класс | URL | Описание |
|-------|-----|----------|
| `LatestNewsFeed` | `/news/feed/` | Последние активные новости |
| `NewsByCategoryFeed` | `/news/feed/<slug>/` | Новости по категории |

---

## 🗺 URL-маршруты

Пространство имён: `news`

| Имя | URL |
|-----|-----|
| `news:list` | `/news/` |
| `news:detail` | `/news/<slug>/` |
| `news:category` | `/news/category/<slug>/` |
| `news:search` | `/news/search/` |
| `news:by_tag` | `/news/tag/<slug>/` |
