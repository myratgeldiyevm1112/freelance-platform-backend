# 🚀 Freelance Platform API

> Production-grade REST API for a freelance marketplace — built with Clean Architecture, async Python, and modern DevOps practices.

![CI](https://github.com/myratgeldiyevm1112/freelance-platform-backend/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136-green)
![Coverage](https://img.shields.io/badge/coverage-83%25-brightgreen)
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
- **Professional testing** — 84 tests, 83% coverage
- **CI/CD** with GitHub Actions + Render deployment
- **Production features** — Redis caching, rate limiting, Celery, WebSockets, S3

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.136 |
| Database | PostgreSQL + SQLAlchemy (async) |
| Migrations | Alembic |
| Auth | JWT (access + refresh tokens) |
| Caching | Redis (jobs list, ratings, refresh tokens) |
| Background Tasks | Celery + Redis broker |
| File Storage | AWS S3 / MinIO |
| Real-time | WebSockets |
| Validation | Pydantic v2 |
| Rate Limiting | SlowAPI |
| Testing | Pytest + pytest-asyncio (84 tests) |
| Linting | Ruff |
| CI/CD | GitHub Actions + Render |
| Containerization | Docker + Docker Compose |

---

## 🎯 Features

### Auth
- User registration (client / freelancer roles)
- Login with JWT access & refresh tokens
- Refresh token stored in Redis (logout support)
- Rate limiting: 5/min register, 10/min login

### Jobs
- Create job postings (clients only)
- List & filter jobs by status, budget, skill (with pagination)
- Full-text search by title/description (PostgreSQL tsvector)
- Redis caching (TTL 60s, invalidated on create/update)

### Proposals
- Submit proposals to jobs (freelancers only)
- Accept / reject proposals (clients only)
- Duplicate proposal prevention
- Real-time WebSocket notifications on submit/accept

### Contracts
- Auto-created when proposal is accepted
- Status lifecycle: `active` → `completed` / `cancelled`
- Email notification via Celery background task

### Reviews
- Leave reviews after contract completion
- Rating system (1–5 stars)
- Average rating aggregation per user (Redis cached, TTL 5min)

### Skills
- Add/remove skills to profile
- Filter jobs by required skill
- Many-to-many user-skills relation

### File Upload
- Avatar upload (JPG/PNG, max 5MB)
- Portfolio upload (JPG/PNG/PDF, max 5MB per file)
- Stored in S3/MinIO, URL saved to profile

### WebSockets
- Real-time notifications: `proposal_submitted`, `proposal_accepted`
- JWT authentication on handshake
- Multiple connections per user supported

---

## 🏗️ Architecture

![Architecture](./architecture.svg)

This project follows **Clean Architecture** principles:

```
api/             ← HTTP layer (routers, dependencies)
    ↓
application/     ← Business logic (use cases, DTOs, interfaces)
    ↓
domain/          ← Core entities and exceptions (no dependencies)
    ↑
infrastructure/  ← DB models, repositories, Redis, S3, Celery, WebSocket
```

**Dependency rule:** outer layers depend on inner layers. Domain knows nothing about FastAPI or SQLAlchemy.

---

## 📬 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login, get tokens |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/logout` | Logout, invalidate refresh token |
| GET | `/api/v1/users/me` | Get my profile |
| PATCH | `/api/v1/users/me` | Update my profile |
| POST | `/api/v1/users/me/avatar` | Upload avatar (JPG/PNG) |
| POST | `/api/v1/users/me/portfolio` | Upload portfolio files |
| POST | `/api/v1/users/me/skills` | Add skills to profile |
| GET | `/api/v1/users/me/skills` | Get my skills |
| DELETE | `/api/v1/users/me/skills/{skill_id}` | Remove skill |
| POST | `/api/v1/jobs/` | Create job (client) |
| GET | `/api/v1/jobs/` | List jobs (paginated, filterable, searchable) |
| GET | `/api/v1/jobs/{job_id}` | Get job by ID |
| POST | `/api/v1/proposals/jobs/{job_id}/proposals` | Submit proposal |
| GET | `/api/v1/proposals/jobs/{job_id}/proposals` | List proposals |
| PATCH | `/api/v1/proposals/{proposal_id}` | Accept/reject proposal |
| GET | `/api/v1/contracts/{contract_id}` | Get contract |
| PATCH | `/api/v1/contracts/{contract_id}/status` | Update contract status |
| POST | `/api/v1/reviews/` | Leave review |
| GET | `/api/v1/reviews/user/{user_id}` | Get user reviews |
| GET | `/api/v1/reviews/user/{user_id}/rating` | Get user rating |
| WS | `/api/v1/ws/{user_id}?token=...` | WebSocket real-time notifications |

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
Flower (Celery monitor): `http://localhost:5555`  
MailHog (email preview): `http://localhost:8025`  
MinIO (file storage): `http://localhost:9001`

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

**84 tests** — unit + integration, **83% coverage**

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
CELERY_BROKER_URL=redis://localhost:6380/0
AWS_ACCESS_KEY=your-access-key
AWS_SECRET_KEY=your-secret-key
S3_BUCKET=freelance-platform
S3_ENDPOINT_URL=http://localhost:9000
```

---

## 👤 Author

**Muhammet Myratgeldiyev**

- GitHub: [@myratgeldiyevm1112](https://github.com/myratgeldiyevm1112)
- LinkedIn: [Muhammet Myratgeldiyev](https://www.linkedin.com/in/muhammet-myratgeldiyev-aa8736413)

---

## 📝 License

MIT