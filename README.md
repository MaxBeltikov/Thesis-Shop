# Django + React: базовый логин (JWT)

## Запуск

### 1) Backend

```powershell
cd <папка_проекта>

# (один раз) зависимости
.\.venv\Scripts\pip install -r requirements.txt

# миграции + запуск
.\.venv\Scripts\python backend\manage.py migrate
.\.venv\Scripts\python backend\manage.py runserver 8000
```

API: `http://127.0.0.1:8000/api/`

### 2) Frontend

```powershell
cd <папка_проекта>\frontend
npm install
npm run dev
```

Сайт: `http://localhost:5173/`

## Страницы
- `/login`
- `/register`
- `/dashboard` (после логина)

## API (auth)
- `POST /api/auth/register/`
- `POST /api/auth/login/` → `access` + `refresh`
- `POST /api/auth/refresh/`
- `GET /api/auth/me/` (Bearer access)

## База данных
По умолчанию **SQLite** (настройка в `backend/.env`).
