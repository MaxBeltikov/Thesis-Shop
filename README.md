# ИС электронной коммерции (Django + React)

## Запуск

### Запуск одной командой (Docker)

Требуется установленный Docker Desktop.

```powershell
cd <папка_проекта>
copy .env.example .env
docker compose up --build
```

- Frontend: `http://localhost:5173/`
- Backend API: `http://127.0.0.1:8000/api/`
- PostgreSQL: `localhost:5432` (внутри docker-compose)

Остановка:

```powershell
docker compose down
```

### Backend

```powershell
cd <папка_проекта>
pip install -r requirements.txt
cd backend
copy .env.example .env
python manage.py migrate
python manage.py load_demo
python manage.py runserver 8000
```

API: `http://127.0.0.1:8000/api/`

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Сайт: `http://localhost:5173/`

## Демо-учётки (после `load_demo`)

- Клиент: `demo.client@example.com` / `demo1234`
- Менеджер: `demo.manager@example.com` / `demo1234`

## API

### Auth
- `POST /api/auth/register/`
- `POST /api/auth/login/` → `access` + `refresh`
- `POST /api/auth/refresh/`
- `GET /api/auth/me/`

### Каталог, заказы
- `GET/POST /api/catalog/products/`
- `GET /api/catalog/products/?search=<строка>` — поиск по названию
- `GET/POST /api/orders/`
- `GET /api/orders/?search=<строка>` — поиск по номеру/статусу/email
- `GET /api/orders/{id}/documents/` — документы заказа

### Документы
- `GET/POST /api/documents/`
- `POST /api/documents/{id}/send/` — отправить
- `POST /api/documents/{id}/sign/` — подписать (`{"password": "..."}`)
- `POST /api/documents/{id}/reject/` — отклонить
- `POST /api/documents/{id}/create-next/` — КП → счёт → акт
- `POST /api/documents/{id}/generate/` — перегенерировать docx/pdf

### Отчёты (менеджер/админ)
- `GET /api/reports/orders/export/` — Excel заказов
- `GET /api/reports/documents/export/` — Excel документов
- `GET /api/reports/orders/export.csv` — CSV заказов
- `GET /api/reports/documents/export.csv` — CSV документов

## Тесты

```powershell
py -3.12 -m pytest backend/tests -v
```

## База данных

PostgreSQL — параметры в `backend/.env`.
