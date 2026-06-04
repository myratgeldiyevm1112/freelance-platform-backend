# 🚀 Freelance Platform API

> Production-grade REST API for a freelance marketplace — built with Clean Architecture, async Python, and modern DevOps practices.

![CI](https://github.com/myratgeldiyevm1112/freelance-platform-backend/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136-green)
![Coverage](https://img.shields.io/badge/coverage-86%25-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)

**Live API:** https://freelance-platform-backend-gkyj.onrender.com/docs

---

## 📌 Overview

Freelance Platform is a backend API that powers a marketplace where **clients post jobs** and **freelancers submit proposals**. Inspired by platforms like Upwork, it covers the full lifecycle:

```
Register → Post Job → Submit Proposal → Accept → Contract → Complete → Review
```

Built as a portfolio project demonstrating:
- **Clean Architecture** with clear separation of concerns
- **Async Python** with FastAPI + SQLAlchemy
- **Professional testing** — 48 tests, 86% coverage
- **CI/CD** with GitHub Actions + Render deployment

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.136 |
| Database | PostgreSQL + SQLAlchemy (async) |
| Migrations | Alembic |
| Auth | JWT (access + refresh tokens) |
| Validation | Pydantic v2 |
| Testing | Pytest + pytest-asyncio (48 tests) |
| Linting | Ruff |
| CI/CD | GitHub Actions + Render |
| Containerization | Docker + Docker Compose |

---

## 🎯 Features

### Auth
- User registration (client / freelancer roles)
- Login with JWT access & refresh tokens
- Role-based access control

### Jobs
- Create job postings (clients only)
- List & filter jobs by status, budget (with pagination)
- Job status lifecycle: `open` → `in_progress` → `closed`

### Proposals
- Submit proposals to jobs (freelancers only)
- Accept / reject proposals (clients only)
- Duplicate proposal prevention

### Contracts
- Auto-created when proposal is accepted
- Status lifecycle: `active` → `completed` / `cancelled`

### Reviews
- Leave reviews after contract completion
- Rating system (1–5 stars)
- Average rating aggregation per user

---

## 🏗️ Architecture

This project follows **Clean Architecture** principles:

```
api/             ← HTTP layer (routers, dependencies)
    ↓
application/     ← Business logic (use cases, DTOs, interfaces)
    ↓
domain/          ← Core entities and exceptions (no dependencies)
    ↑
infrastructure/  ← DB models, repositories, external services
```

**Dependency rule:** outer layers depend on inner layers. Domain knows nothing about FastAPI or SQLAlchemy.

---

## 📬 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login, get tokens |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| GET | `/api/v1/users/me` | Get my profile |
| PATCH | `/api/v1/users/me` | Update my profile |
| POST | `/api/v1/jobs/` | Create job (client) |
| GET | `/api/v1/jobs/` | List jobs (paginated) |
| GET | `/api/v1/jobs/{job_id}` | Get job by ID |
| POST | `/api/v1/proposals/jobs/{job_id}/proposals` | Submit proposal |
| GET | `/api/v1/proposals/jobs/{job_id}/proposals` | List proposals |
| PATCH | `/api/v1/proposals/{proposal_id}` | Accept/reject proposal |
| GET | `/api/v1/contracts/{contract_id}` | Get contract |
| PATCH | `/api/v1/contracts/{contract_id}/status` | Update contract status |
| POST | `/api/v1/reviews/` | Leave review |
| GET | `/api/v1/reviews/user/{user_id}` | Get user reviews |
| GET | `/api/v1/reviews/user/{user_id}/rating` | Get user rating |

Full interactive docs: https://freelance-platform-backend-gkyj.onrender.com/docs

---

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.12+

### Run with Docker

```bash
git clone https://github.com/myratgeldiyevm1112/freelance-platform-backend.git
cd freelance-platform-backend
cp .env.example .env
docker-compose up --build
```

API: `http://localhost:8000`  
Docs: `http://localhost:8000/docs`

### Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=app --cov-report=term-missing

# Unit tests only
pytest tests/unit/ -v
```

**48 tests** — unit + integration, **86% coverage**

---

## 📄 Environment Variables

```env
APP_ENV=development
DEBUG=True
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5433/freelance_db
REDIS_URL=redis://localhost:6380
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALLOWED_ORIGINS=["http://localhost:3000"]
```

---

## 👤 Author

**Muhammet Myratgeldiyev**

- GitHub: [@myratgeldiyevm1112](https://github.com/myratgeldiyevm1112)
- LinkedIn: [Muhammet Myratgeldiyev](https://www.linkedin.com/in/muhammet-myratgeldiyev-aa8736413)

---

## 📝 License

MIT