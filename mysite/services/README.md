# Приложение `services` — Услуги

Каталог предоставляемых услуг с гибкой системой ценообразования, мультивалютностью, корзиной и подсчётом просмотров.

---

## 📁 Структура файлов

```
services/
├── models.py           # Модели: ServiceCategory, Service
├── views.py            # Представления
├── urls.py             # URL-маршруты
├── admin.py            # Конфигурация Django Admin
├── apps.py             # Конфигурация приложения
├── cart.py             # Корзина услуг (сессионная)
├── cart_views.py       # Представления корзины
├── context_processors.py  # Контекст корзины
├── signals.py          # Django-сигналы (очистка медиафайлов)
├── migrations/         # Миграции базы данных
├── static/             # CSS, JS
├── templatetags/       # Кастомные теги шаблонов
└── templates/services/ # HTML-шаблоны
```

---

## 📦 Модели (`models.py`)

### `ServiceCategory` — Категория услуг

Наследует `HeroMixin` (поля Hero-баннера).

| Поле | Тип | Описание |
|------|-----|----------|
| `name` | CharField(100) | Название категории |
| `slug` | SlugField | Уникальный URL (автогенерация) |
| `image` | ImageField | Изображение (`services/categories/`) |
| `description` | CKEditor5Field | Описание WYSIWYG |
| `seo_title` | CharField(200) | SEO-заголовок |
| `seo_keywords` | CharField(200) | SEO-ключевые слова |
| `seo_description` | CharField(255) | SEO-описание |
| `show_in_menu` | BooleanField | Показывать в меню (default: True) |
| `order` | IntegerField | Порядок сортировки |
| `is_active` | BooleanField | Активность (default: True) |
| `views` | PositiveIntegerField | Счётчик просмотров |
| `created_at/updated_at` | DateTimeField | Временны́е метки |

**Методы:**
- `save()` — автогенерация уникального slug
- `get_absolute_url()` → `/services/category/<slug>/`
- `services_count()` — количество услуг в категории

**Сортировка:** `["order", "name"]`

---

### `Service` — Услуга

Наследует `HeroMixin`.

**Типы цен (`PRICE_TYPE_CHOICES`):**
| Значение | Отображение |
|---------|-------------|
| `fixed` | Фиксированная цена |
| `from` | От (минимальная) |
| `to` | До (максимальная) |
| `range` | Диапазон «от — до» |

**Валюты (`CURRENCY_CHOICES`):**

| Значение | Символ |
|---------|--------|
| `RUB` | ₽ |
| `USD` | $ |
| `EUR` | € |
| `KZT` | ₸ |

| Поле | Тип | Описание |
|------|-----|----------|
| `name` | CharField(200) | Название услуги |
| `slug` | SlugField | Уникальный URL |
| `category` | ForeignKey→ServiceCategory | Категория (CASCADE) |
| `short_description` | CKEditor5Field | Краткое описание |
| `description` | CKEditor5Field | Полное описание |
| `icon` | ImageField | Иконка услуги (`services/icons/`) |
| `background` | ImageField | Фоновое изображение (`services/backgrounds/`) |
| `price_type` | CharField | Тип ценообразования |
| `price_fixed` | DecimalField | Фиксированная цена |
| `price_from` | DecimalField | Цена «от» |
| `price_to` | DecimalField | Цена «до» |
| `currency` | CharField | Валюта (default: RUB) |
| `can_order` | BooleanField | Можно заказать |
| `is_displayed` | BooleanField | Отображается на сайте |
| `seo_*` | CharField | SEO-поля |
| `views` | PositiveIntegerField | Счётчик просмотров |
| `created_at/updated_at` | DateTimeField | Временны́е метки |

**Ключевые методы:**
- `save()` — автогенерация уникального slug
- `get_absolute_url()` → `/services/<slug>/`
- `get_price_display()` — форматированная строка цены (например: `«от 5 000 ₽»`)
- `increment_views()` — атомарный счётчик через `F("views") + 1`

**Сортировка:** `["-created_at"]`

---

## 🌐 Представления (`views.py` и `cart_views.py`)

| Функция/Класс | URL | Описание |
|---------------|-----|----------|
| `service_list` | `/services/` | Каталог услуг. Фильтр по категории, поиск, пагинация |
| `service_detail` | `/services/<slug>/` | Детальная страница услуги + похожие услуги |
| `service_category` | `/services/category/<slug>/` | Услуги по категории |
| `cart_add` | `/services/cart/add/` | Добавление в корзину (POST) |
| `cart_remove` | `/services/cart/remove/<id>/` | Удаление из корзины |
| `cart_detail` | `/services/cart/` | Просмотр корзины |

---

## 🛒 Корзина услуг (`cart.py`)

Сессионная корзина без моделей базы данных.

**Класс `Cart`:**
- `add(service, quantity)` — добавление услуги
- `remove(service)` — удаление услуги
- `clear()` — очистка корзины
- `__iter__()` — итерация по товарам
- `__len__()` — количество товаров

---

## 🗺 URL-маршруты

Пространство имён: `services`

| Имя | URL |
|-----|-----|
| `services:list` | `/services/` |
| `services:detail` | `/services/<slug>/` |
| `services:category` | `/services/category/<slug>/` |
| `services:cart_add` | `/services/cart/add/` |
| `services:cart_remove` | `/services/cart/remove/<id>/` |
| `services:cart_detail` | `/services/cart/` |
