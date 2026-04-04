# Приложение `accounts` — Пользователи и Тикеты

Управление профилями пользователей, аутентификация (вход по email или username) и система технической поддержки через тикеты.

---

## 📁 Структура файлов

```
accounts/
├── models.py           # Модели: UserProfile, Ticket, TicketResponse
├── views.py            # Представления
├── urls.py             # URL-маршруты
├── forms.py            # Формы регистрации, входа, профиля, тикетов
├── admin.py            # Конфигурация Django Admin
├── apps.py             # Конфигурация приложения
├── backends.py         # Кастомный backend — вход по email
├── context_processors.py  # Контекст профиля пользователя
├── mixins.py           # Миксины прав доступа
├── signals.py          # Сигнал автосоздания профиля
├── utils.py            # Вспомогательные функции
├── migrations/         # Миграции базы данных
├── static/             # CSS, JS, изображения
└── templates/accounts/ # HTML-шаблоны
```

---

## 📦 Модели (`models.py`)

### Функция `avatar_upload_path`
Генерирует путь для сохранения аватара: `avatars/avatar_user_<id>.<ext>`.
Допустимые расширения: `jpg`, `jpeg`, `png`, `gif`. При недопустимом расширении — `ValueError`.

---

### `UserProfile` — Профиль пользователя

**Назначение:** Расширение стандартной модели `User` дополнительными полями.

| Поле | Тип | Описание |
|------|-----|----------|
| `user` | OneToOneField→User | Связь с пользователем (CASCADE). Обратная: `user.profile` |
| `phone` | CharField(20) | Телефон. Формат: `+7 XXX XXX-XX-XX` |
| `avatar` | ImageField | Аватар пользователя |
| `bio` | TextField(1000) | Биография/О себе |
| `created_at` | DateTimeField | Дата создания (auto_now_add) |
| `updated_at` | DateTimeField | Дата обновления (auto_now) |

**Свойства:**
- `get_avatar_url` — URL аватара или `/static/accounts/images/default-avatar.png`

**Валидация (`clean`):** телефон должен начинаться с `'+'`

**Сортировка:** `["-created_at"]`

---

### Сигнал `create_or_update_user_profile`

Автоматически создаёт `UserProfile` при создании нового `User` (сигнал `post_save`). При обновлении — обновляет существующий профиль или создаёт, если отсутствует. Ошибки записываются в лог (`logger.error`).

---

### `Ticket` — Тикет поддержки

**Назначение:** Система обращений пользователей в службу поддержки.

**Статусы:**
| Константа | Значение | Описание |
|-----------|---------|----------|
| `STATUS_OPEN` | `open` | Тикет открыт (новый) |
| `STATUS_IN_PROGRESS` | `in_progress` | Тикет в обработке |
| `STATUS_CLOSED` | `closed` | Тикет закрыт (решён) |

| Поле | Тип | Описание |
|------|-----|----------|
| `user` | ForeignKey→User | Автор тикета. Обратная: `user.tickets` |
| `subject` | CharField(200) | Тема тикета |
| `message` | TextField | Текст обращения |
| `status` | CharField | Статус из `STATUS_CHOICES` (default: `open`) |
| `created_at` | DateTimeField | Дата создания (auto) |
| `updated_at` | DateTimeField | Дата обновления (auto) |

**Свойства:**
- `is_open` → `True` если статус = `open`
- `is_closed` → `True` если статус = `closed`

**Методы:**
- `get_absolute_url()` → `/accounts/tickets/<pk>/`
- `can_user_access(user)` → `True` если `user == ticket.user` или `user.is_staff`

**Индексы БД:** `["status", "created_at"]`, `["user", "created_at"]`

---

### `TicketResponse` — Ответ на тикет

**Назначение:** Переписка в рамках тикета.

| Поле | Тип | Описание |
|------|-----|----------|
| `ticket` | ForeignKey→Ticket | Тикет. Обратная: `ticket.responses` |
| `user` | ForeignKey→User | Автор ответа |
| `message` | TextField | Текст ответа |
| `is_admin_response` | BooleanField | Ответ от персонала (автоустанавливается) |
| `created_at` | DateTimeField | Дата создания (auto) |

**Логика (`save`):** если `user.is_staff` → `is_admin_response = True`

**Валидация:** сообщение не может быть пустым (`message.strip()`)

**Сортировка:** `["created_at"]` (хронологический порядок)

---

## 🌐 Представления (`views.py`)

| Функция | URL | Описание |
|---------|-----|----------|
| `register` | `/accounts/register/` | Регистрация нового пользователя |
| `LoginView` | `/accounts/login/` | Вход (стандартный Django + CustomAuthenticationForm с капчей) |
| `custom_logout` | `/accounts/logout/` | Выход (только POST) |
| `logout_confirmation` | `/accounts/logout/confirm/` | Страница подтверждения выхода |
| `profile_view` | `/accounts/profile/` | Личный кабинет |
| `profile_edit` | `/accounts/profile/edit/` | Редактирование имени и email |
| `profile_update` | `/accounts/profile/update/` | Обновление аватара, телефона, биографии |
| `password_change` | `/accounts/password/change/` | Смена пароля |
| `ticket_list` | `/accounts/tickets/` | Список тикетов пользователя |
| `create_ticket` | `/accounts/tickets/create/` | Создание нового тикета |
| `ticket_detail` | `/accounts/tickets/<pk>/` | Просмотр тикета и диалог ответов |

---

## 📝 Формы (`forms.py`)

| Форма | Назначение |
|-------|-----------|
| `CustomAuthenticationForm` | Форма входа с капчей (`django-simple-captcha`) |
| `RegistrationForm` | Форма регистрации (username, email, password, капча) |
| `ProfileEditForm` | Редактирование имени и фамилии, email |
| `ProfileUpdateForm` | Обновление аватара, телефона, биографии |
| `PasswordChangeForm` | Смена пароля с подтверждением |
| `TicketForm` | Создание нового тикета |
| `TicketResponseForm` | Добавление ответа к тикету |

---

## 🔧 Дополнительные файлы

### `backends.py` — Аутентификация по email
Кастомный аутентификационный backend позволяет входить в систему как по `username`, так и по `email`.

### `mixins.py`
Миксины проверки прав доступа для представлений на основе классов.

### `context_processors.py`
Добавляет `user_profile` в глобальный контекст шаблонов для всех страниц.

---

## 🗺 URL-маршруты (`urls.py`)

Пространство имён: `accounts`

| Имя | URL |
|-----|-----|
| `accounts:register` | `/accounts/register/` |
| `accounts:login` | `/accounts/login/` |
| `accounts:logout` | `/accounts/logout/` |
| `accounts:logout_confirm` | `/accounts/logout/confirm/` |
| `accounts:profile` | `/accounts/profile/` |
| `accounts:profile_edit` | `/accounts/profile/edit/` |
| `accounts:profile_update` | `/accounts/profile/update/` |
| `accounts:password_change` | `/accounts/password/change/` |
| `accounts:ticket_list` | `/accounts/tickets/` |
| `accounts:create_ticket` | `/accounts/tickets/create/` |
| `accounts:ticket_detail` | `/accounts/tickets/<pk>/` |
