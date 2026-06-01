# 🚀 Freelance Platform Backend

> A clean, production-grade REST API for a freelance marketplace — built with modern Python backend practices.

---

## 📌 Overview

**Freelance Platform** is a backend API that powers a marketplace where **clients post jobs** and **freelancers submit proposals**. Inspired by platforms like Upwork, it covers the full lifecycle: job posting → proposals → contracts → reviews.

Built as a portfolio project demonstrating Clean Architecture, async Python, and professional API design.

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy (async) |
| Migrations | Alembic |
| Cache | Redis |
| Auth | JWT (OAuth2 Bearer) |
| Testing | Pytest + pytest-asyncio |
| Containerization | Docker + Docker Compose |

---

## 🎯 MVP Features

### Auth
- [x] User registration (client / freelancer)
- [x] Login with JWT access & refresh tokens
- [x] Role-based access control

### Users
- [x] Profile management
- [x] Freelancer profile (skills, bio, rate)
- [x] Client profile

### Jobs
- [x] Create / update / delete job posting (client)
- [x] List & filter jobs (freelancer)
- [x] Job status management (`open`, `in_progress`, `closed`)

### Proposals
- [x] Submit proposal to a job (freelancer)
- [x] Accept / reject proposal (client)
- [x] Proposal status (`pending`, `accepted`, `rejected`)

### Contracts
- [x] Auto-created when proposal is accepted
- [x] Contract status (`active`, `completed`, `cancelled`)

### Reviews
- [x] Leave review after contract completion
- [x] Rating system (1–5)

---

## 🏗️ Architecture

This project follows **Clean Architecture** principles with clear separation of concerns:

```
app/
├── domain/          # Entities, value objects, domain exceptions
├── application/     # Use cases, interfaces, DTOs
├── infrastructure/  # DB models, repositories, external services
├── api/             # FastAPI routers, request/response schemas
└── core/            # Config, security, logging, dependencies
```

**Dependency rule:** `api → application → domain` (domain knows nothing about the outside world)

---

## 📁 Project Structure

```
freelance-platform-backend/
├── app/
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   ├── api/
│   └── core/
├── tests/
├── alembic/
├── docker/
├── .env.example
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.11+

### Run with Docker

```bash
git clone https://github.com/yourusername/freelance-platform-backend.git
cd freelance-platform-backend
cp .env.example .env
docker-compose up --build
```

API will be available at: `http://localhost:8000`

Interactive docs: `http://localhost:8000/docs`

### Run locally

```bash
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload
```

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

---

## 📄 Environment Variables

```env
# App
APP_ENV=development
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/freelance_db

# Redis
REDIS_URL=redis://localhost:6379

# CORS
ALLOWED_ORIGINS=http://localhost:3000
```

---

## 📬 API Endpoints (Overview)

```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh

GET    /api/v1/users/me
PATCH  /api/v1/users/me

POST   /api/v1/jobs/
GET    /api/v1/jobs/
GET    /api/v1/jobs/{job_id}
PATCH  /api/v1/jobs/{job_id}
DELETE /api/v1/jobs/{job_id}

POST   /api/v1/jobs/{job_id}/proposals
GET    /api/v1/jobs/{job_id}/proposals
PATCH  /api/v1/proposals/{proposal_id}

GET    /api/v1/contracts/{contract_id}
PATCH  /api/v1/contracts/{contract_id}

POST   /api/v1/reviews/
GET    /api/v1/reviews/user/{user_id}
```

---

## 👤 Author

Built by **Muhammet Myratgeldiyev** as a portfolio project.

- GitHub: [@myratgeldiyevm1112](https://github.com/myratgeldiyevm1112)
- LinkedIn: [yourprofile](https://linkedin.com/in/yourprofile)

---

## 📝 License

MIT
