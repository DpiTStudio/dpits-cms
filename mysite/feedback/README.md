# Приложение `feedback` — Обратная связь

Форма обратной связи для зарегистрированных пользователей с email-уведомлениями администратору и системой статусов обработки.

---

## 📁 Структура файлов

```
feedback/
├── models.py           # Модель FeedbackMessage
├── views.py            # Представления
├── urls.py             # URL-маршруты
├── forms.py            # Форма обратной связи
├── admin.py            # Конфигурация Django Admin
├── apps.py             # Конфигурация приложения
├── migrations/         # Миграции базы данных
└── templates/feedback/ # HTML-шаблоны
```

---

## 📦 Модели (`models.py`)

### `FeedbackMessage` — Сообщение обратной связи

**Статусы:**

| Константа | Значение | Описание |
|-----------|---------|----------|
| `STATUS_NEW` | `new` | Новое — не прочитано (default) |
| `STATUS_READ` | `read` | Прочитано администратором |
| `STATUS_REPLIED` | `replied` | Получен ответ |
| `STATUS_ARCHIVED` | `archived` | Архивировано |

| Поле | Тип | Описание |
|------|-----|----------|
| `user` | ForeignKey→User | Автор сообщения (CASCADE). Обратная: `user.feedback_messages` |
| `subject` | CharField(200) | Тема сообщения |
| `message` | TextField | Текст сообщения |
| `email` | EmailField(254) | Email для ответа |
| `status` | CharField(20) | Статус обработки (default: `new`) |
| `admin_notes` | TextField | Внутренние заметки администратора |
| `created_at` | DateTimeField | Дата создания (auto_now_add) |
| `updated_at` | DateTimeField | Дата обновления (auto_now) |
| `email_sent` | BooleanField | Отправлено ли email-уведомление |

**Свойства:**
- `is_new` → `True` если `status == "new"`
- `is_read` → `True` если `status == "read"`

**Методы:**
- `get_absolute_url()` → `/feedback/<pk>/`
- `can_user_access(user)` → `True` если `user == message.user` или `user.is_staff`

**Индексы БД:** `["status", "created_at"]`, `["user", "created_at"]`

**Мета-настройки:**
- `verbose_name`: «Сообщение обратной связи» / «Обратная связь»
- `ordering`: `["-created_at"]`

---

## 🌐 Представления (`views.py`)

| Функция/Класс | URL | Описание |
|---------------|-----|----------|
| `feedback_create` | `/feedback/` | Форма отправки сообщения (только авторизованные) |
| `feedback_detail` | `/feedback/<pk>/` | Просмотр своего сообщения |
| `feedback_list` | `/feedback/list/` | Список своих сообщений с историей |

---

## 📝 Формы (`forms.py`)

**`FeedbackForm`** — форма отправки обратной связи:
- Поля: `subject`, `message`, `email`
- Требует авторизации пользователя
- После отправки: создаётся запись + при необходимости отправляется email-уведомление администратору

---

## ⚙️ Администрирование (`admin.py`)

В Django Admin доступно:
- Просмотр всех сообщений с фильтром по статусу
- Изменение статуса: новое → прочитано → отвечено → архив
- Поле `admin_notes` для внутренних заметок
- Просмотр `email_sent` (факт отправки уведомления)

---

## 🗺 URL-маршруты (`urls.py`)

Пространство имён: `feedback`

| Имя | URL | Описание |
|-----|-----|----------|
| `feedback:create` | `/feedback/` | Форма отправки |
| `feedback:detail` | `/feedback/<pk>/` | Просмотр сообщения |
| `feedback:list` | `/feedback/list/` | Список сообщений |

---

## 💡 Отличие от приложения `reviews`

| Параметр | `feedback` | `reviews` |
|----------|-----------|----------|
| Требует регистрации | Да | Нет |
| Виден другим | Нет (личные сообщения) | Да (публичные отзывы) |
| Email уведомление | Да | Нет |
| Модерация | Статус обработки | Одобрение/отклонение |
