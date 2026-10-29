# BudgetBuddy — Student Budget Planning and Expense Management

A full-stack starter implementation based on the supplied project specification.

## Stack
- Frontend: React + Vite + React Router + Axios + Recharts
- Backend: Python + Django + Django REST Framework
- Authentication: JWT using SimpleJWT
- Local database: SQLite
- Optional production database: PostgreSQL (configuration notes below)

## Features included
- Register/login with JWT
- Dashboard summary and monthly spending chart
- Add/list/edit/delete expenses and income
- Category-wise monthly budgets and utilization
- Savings goals and progress tracking
- Notifications generated for budget overspending
- CSV export for expenses and income
- Django admin for managing records

## Requirements
- Python 3.10+
- Node.js 18+
- npm

## 1. Run the backend
Open a terminal in `backend/`:

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Backend runs at `http://127.0.0.1:8000/`.
API root: `http://127.0.0.1:8000/api/`.

## 2. Run the frontend
Open a second terminal in `frontend/`:

```bash
npm install
npm run dev
```

Frontend runs at `http://localhost:5173/`.

## 3. First use
Register a new account from the app. The app stores the JWT access/refresh tokens in localStorage for this development version. Do not use this storage strategy without reviewing security requirements for a production deployment.

## Main API routes
- `POST /api/auth/register/`
- `POST /api/auth/token/`
- `POST /api/auth/token/refresh/`
- `GET/PATCH /api/profile/`
- `GET/POST /api/expenses/`
- `GET/PATCH/DELETE /api/expenses/<id>/`
- `GET/POST /api/incomes/`
- `GET/PATCH/DELETE /api/incomes/<id>/`
- `GET/POST /api/budgets/`
- `GET/PATCH/DELETE /api/budgets/<id>/`
- `GET/POST /api/goals/`
- `GET/PATCH/DELETE /api/goals/<id>/`
- `GET /api/notifications/`
- `GET /api/dashboard/`
- `GET /api/reports/expenses.csv`
- `GET /api/reports/incomes.csv`

## Production notes
The supplied specification mentions PostgreSQL, deployment, OAuth2, push/email notifications, PDF/Excel exports, and automated testing. This starter implements the core workflows locally and includes CSV export. Before production, configure PostgreSQL and secure secrets/CORS, add OAuth2 and email/push delivery, implement PDF/XLSX exports, add tests, and deploy frontend/backend separately.
