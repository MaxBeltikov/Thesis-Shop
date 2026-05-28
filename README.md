# Информационная система электронной коммерции для малого бизнеса

Веб‑сервис для автоматизации продаж и коммерческого документооборота малого бизнеса. Позволяет вести каталог товаров/услуг, формировать заказы и автоматически генерировать документы по сделке (КП, счёт, акт, накладная). Документы формируются в **DOCX/PDF** и учитываются в системе (статусы, подпись, аудит). Предусмотрен **REST API** для интеграции с внешними системами (сайт/CRM/внутренний портал).

Основная цель — сократить ручной труд при подготовке коммерческих документов и обеспечить единый учёт заказов и документов.

---

## Стек

| Слой | Технология |
|------|------------|
| **Бэкенд** | Python, Django, Django REST Framework |
| **Аутентификация** | JWT (SimpleJWT) |
| **База данных** | PostgreSQL (Docker), SQLite (для тестов) |
| **Генерация документов** | python-docx (DOCX), reportlab (PDF) |
| **Экспорт** | openpyxl (Excel), CSV (HTTP export) |
| **Фронтенд** | React (Vite), React Router, Axios |
| **Тестирование** | pytest, pytest-django |
| **Инфраструктура** | Docker, docker-compose, Git |

---

## Ключевые возможности

### Пользователи и доступы (RBAC)
- Роли: **client / manager / admin**
- Клиент видит только свои заказы/документы
- Менеджер/админ видят все сущности и могут выполнять операции записи

### Каталог
- CRUD товаров/услуг
- Поиск по названию: `GET /api/catalog/products/?search=<строка>`

### Заказы
- Создание заказа с вложенными позициями
- Автоматический расчёт итоговой суммы
- Поиск: `GET /api/orders/?search=<строка>` (номер/статус/email)

### Документы и документооборот
- Типы документов: **КП / счёт / акт / накладная**
- Жизненный цикл: **черновик → отправлен → подписан / отклонён**
- Цепочка: **КП → счёт → акт** (Model A: без создания дублей следующего документа)
- Связи документов: `parent/children` (видно, от какого документа создан следующий)

### Генерация файлов
- Автогенерация **DOCX + PDF** при создании документа
- Возможность перегенерации по кнопке/эндпоинту
- Файлы доступны по `/media/...`

### Аудит действий
- Запись значимых действий в `ActionLog` (кто, что, над какой сущностью, когда, IP, детали JSON)

### Отчёты
Экспорт доступен менеджеру/админу:
- Excel:
  - `GET /api/reports/orders/export/`
  - `GET /api/reports/documents/export/`
- CSV:
  - `GET /api/reports/orders/export.csv`
  - `GET /api/reports/documents/export.csv`

---

## Запуск

### Запуск одной командой (Docker) — рекомендовано для демонстрации
Требуется установленный Docker Desktop.

```powershell
cd <папка_проекта>
copy .env.example .env
$env:DOCKER_BUILDKIT="0"
$env:COMPOSE_DOCKER_CLI_BUILD="0"
docker compose up --build
```

- Frontend: `http://localhost:5173/`
- Backend API: `http://127.0.0.1:8000/api/`
- Admin: `http://127.0.0.1:8000/admin/`

Остановка:

```powershell
docker compose down
```

### Локальный запуск (без Docker)

#### Backend
```powershell
cd <папка_проекта>
pip install -r requirements.txt
cd backend
copy .env.example .env
python manage.py migrate
python manage.py load_demo
python manage.py runserver 8000
```

#### Frontend
```powershell
cd <папка_проекта>\frontend
npm install
npm run dev
```

---

## Переменные окружения

### Docker Compose (`.env` в корне проекта)
Файл `.env` **не коммитится**. Пример — `.env.example`:
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `BACKEND_PORT`, `FRONTEND_PORT`

### Backend (`backend/.env`)
Для локального запуска backend используется `backend/.env` (создать копированием `backend/.env.example`).

---

## Демо‑учётки
После `python manage.py load_demo`:
- Клиент: `demo.client@example.com` / `demo1234`
- Менеджер: `demo.manager@example.com` / `demo1234`

---

## REST API (основное)

### Auth
- `POST /api/auth/register/`
- `POST /api/auth/login/` → `access` + `refresh`
- `POST /api/auth/refresh/`
- `GET /api/auth/me/`

### Каталог
- `GET/POST /api/catalog/products/`
- `GET /api/catalog/products/?search=<строка>` — поиск

### Заказы
- `GET/POST /api/orders/`
- `GET /api/orders/?search=<строка>` — поиск
- `GET /api/orders/{id}/documents/` — документы заказа

### Документы
- `GET/POST /api/documents/`
- `POST /api/documents/{id}/send/`
- `POST /api/documents/{id}/sign/` (`{"password": "..."}`)
- `POST /api/documents/{id}/reject/`
- `POST /api/documents/{id}/create-next/` — КП → счёт → акт
- `POST /api/documents/{id}/generate/`
- Шаблоны: `GET/POST /api/documents/templates/`

---

## Тесты

```powershell
py -3.12 -m pytest backend/tests -v
```

---

## Ограничения / заметки (честно)
- Импорт CSV/Excel (массовая загрузка) **не реализован** — есть экспорт отчётов.
- Swagger/OpenAPI авто‑документация **не подключена** (список эндпоинтов приведён в README и в пояснительной записке).
- Генерация документов выполняется **программно** (python-docx/reportlab), а не через заполнение загруженного пользователем docx‑шаблона.
