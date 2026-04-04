# Приложение `knowledge_base` — База Знаний

Раздел справки и документации для пользователей: статьи по категориям, FontAwesome-иконки, счётчик просмотров, отметки полезности и полнотекстовый поиск.

---

## 📁 Структура файлов

```
knowledge_base/
├── models.py           # Модели: Category, Article
├── views.py            # Представления
├── urls.py             # URL-маршруты
├── admin.py            # Конфигурация Django Admin
├── apps.py             # Конфигурация приложения
├── migrations/         # Миграции базы данных
└── templates/          # HTML-шаблоны
    └── knowledge_base/
        ├── category_list.html   # Список разделов
        ├── category_detail.html # Статьи в разделе
        └── article_detail.html  # Чтение статьи
```

---

## 📦 Модели (`models.py`)

### `Category` — Раздел базы знаний

| Поле | Тип | Описание |
|------|-----|----------|
| `name` | CharField(100) | Название раздела |
| `slug` | SlugField(100) | Уникальный URL |
| `description` | TextField | Описание раздела |
| `icon` | CharField(50) | CSS-класс иконки FontAwesome (например: `fas fa-book`) |
| `order` | IntegerField | Порядок сортировки (меньше = выше) |
| `created_at` | DateTimeField | Дата создания |
| `updated_at` | DateTimeField | Дата обновления |

**Методы:**
- `get_absolute_url()` → `/knowledge-base/<slug>/`

**Сортировка:** `["order", "name"]`

---

### `Article` — Статья базы знаний

| Поле | Тип | Описание |
|------|-----|----------|
| `category` | ForeignKey→Category | Раздел (CASCADE). Обратная: `category.articles` |
| `title` | CharField(200) | Заголовок статьи |
| `slug` | SlugField(200) | Уникальный URL |
| `content` | CKEditor5Field | Содержимое (WYSIWYG) |
| `is_published` | BooleanField | Опубликована (default: True) |
| `author` | ForeignKey→User | Автор статьи (SET_NULL, необязательно) |
| `views_count` | PositiveIntegerField | Счётчик просмотров |
| `helpful_count` | PositiveIntegerField | Оценок «Полезно» |
| `not_helpful_count` | PositiveIntegerField | Оценок «Не полезно» |
| `seo_title` | CharField(200) | SEO-заголовок |
| `seo_description` | CharField(255) | SEO-описание |
| `seo_keywords` | CharField(200) | SEO-ключевые слова |
| `created_at` | DateTimeField | Дата создания |
| `updated_at` | DateTimeField | Дата обновления |

**Методы:**
- `get_absolute_url()` → `/knowledge-base/<slug>/` (детальная страница)

**Сортировка:** `["-created_at"]`

---

## 🌐 Представления (`views.py`)

| Класс/Функция | URL | Описание |
|---------------|-----|----------|
| `CategoryListView` | `/knowledge-base/` | Главная страница — список всех разделов с количеством статей |
| `ArticleListView` | `/knowledge-base/<slug>/` | Список опубликованных статей в разделе |
| `ArticleDetailView` | `/knowledge-base/article/<slug>/` | Чтение полной статьи (счётчик просмотров, кнопки «Полезно»/«Не полезно») |

---

## ⚙️ Администрирование (`admin.py`)

- Список статей с фильтром по разделу и статусу публикации
- Редактирование через CKEditor 5
- Отображение счётчиков просмотров и оценок полезности
- Управление порядком разделов

---

## 🗺 URL-маршруты (`urls.py`)

Пространство имён: `knowledge_base`

| Имя | URL | Описание |
|-----|-----|----------|
| `knowledge_base:category_list` | `/knowledge-base/` | Список разделов |
| `knowledge_base:category_detail` | `/knowledge-base/<slug>/` | Статьи раздела |
| `knowledge_base:article_detail` | `/knowledge-base/article/<slug>/` | Текст статьи |

---

## 💡 Особенности

- **Иконки разделов** — хранятся как CSS-классы FontAwesome (например `fas fa-code`), отображаются без загрузки изображений
- **Двойная оценка** — к каждой статье можно отметить «Полезно» или «Не полезно», счётчики хранятся в модели
- **Счётчик просмотров** — `views_count` увеличивается при каждом просмотре статьи
- **Гибкий контент** — полное содержимое через CKEditor 5 с поддержкой таблиц, кода, изображений
