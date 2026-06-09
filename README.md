# 🚀 Freelance Platform API

> Production-grade REST API for a freelance marketplace — built with Clean Architecture, async Python, and modern DevOps practices.

![CI](https://github.com/myratgeldiyevm1112/freelance-platform-backend/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136-green)
![Coverage](https://img.shields.io/badge/coverage-92%25-brightgreen)
![Tests](https://img.shields.io/badge/tests-264-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)

**Live API:** https://freelance-platform-backend-gkyj.onrender.com/docs

---

## 📌 Overview

Freelance Platform is a backend API that powers a marketplace where **clients post jobs** and **freelancers submit proposals**. Inspired by platforms like Upwork and FL.ru, it covers the full lifecycle:

```
Register → Post Job → Submit Proposal → Accept → Contract → Pay (Escrow) → Complete → Review
```

Built as a portfolio project demonstrating:
- **Clean Architecture** with clear separation of concerns
- **Async Python** with FastAPI + SQLAlchemy
- **Professional testing** — 264 tests, 92%+ coverage
- **CI/CD** with GitHub Actions + Render deployment
- **Production features** — Redis caching, rate limiting, Celery, WebSockets, S3, Stripe payments
- **Security** — JWT auth, BOLA protection, role-based access control (admin/client/freelancer)
- **Moderation** — Admin panel with dispute resolution and content moderation

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
| Payments | Stripe (escrow, transfers, refunds) |
| Validation | Pydantic v2 |
| Rate Limiting | SlowAPI |
| Testing | Pytest + pytest-asyncio (264 tests) |
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

### Payments (Stripe Escrow)
- Client pays on proposal acceptance — funds held in escrow
- Release payment to freelancer on contract completion
- Platform commission (10%) automatically withheld
- Refund on contract cancellation
- Stripe webhook handling: `payment_intent.succeeded`, `payment_intent.payment_failed`

### Messaging (Real-time Chat)
- Send messages between client and freelancer per job/contract
- Conversations endpoint with full message history
- Unread message count
- Real-time delivery via WebSocket

### Notifications Center
- System notifications for all platform events (proposals, contracts, payments, messages)
- Mark as read (single)
- Real-time WebSocket push on new notification

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

### Freelancer Search
- Search freelancers by skill, rating and availability
- Public freelancer profiles with portfolio and skills
- `GET /api/v1/freelancers` — paginated search with filters
- `GET /api/v1/freelancers/{user_id}` — public profile

### Disputes
- Open disputes on active contracts
- Admin can resolve disputes
- Full dispute lifecycle management

### Admin Panel
- Ban / unban users
- Delete job postings (moderation)
- Platform statistics dashboard
- Admin-only endpoints with role check

### WebSockets
- Real-time notifications and chat messages
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
infrastructure/  ← DB models, repositories, Redis, S3, Celery, Stripe, WebSocket
```

**Dependency rule:** outer layers depend on inner layers. Domain knows nothing about FastAPI or SQLAlchemy.

---

## 📬 API Endpoints

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login, get tokens |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/logout` | Logout, invalidate refresh token |

### Users & Skills
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/users/me` | Get my profile |
| PATCH | `/api/v1/users/me` | Update my profile |
| POST | `/api/v1/users/me/avatar` | Upload avatar (JPG/PNG) |
| POST | `/api/v1/users/me/portfolio` | Upload portfolio files |
| POST | `/api/v1/users/me/skills` | Add skills to profile |
| GET | `/api/v1/users/me/skills` | Get my skills |
| DELETE | `/api/v1/users/me/skills/{skill_id}` | Remove skill |

### Jobs
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/jobs/` | Create job (client) |
| GET | `/api/v1/jobs/` | List jobs (paginated, filterable, searchable) |
| GET | `/api/v1/jobs/{job_id}` | Get job by ID |

### Proposals & Contracts
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/proposals/jobs/{job_id}/proposals` | Submit proposal |
| GET | `/api/v1/proposals/jobs/{job_id}/proposals` | List proposals |
| PATCH | `/api/v1/proposals/{proposal_id}` | Accept/reject proposal |
| GET | `/api/v1/contracts/{contract_id}` | Get contract |
| PATCH | `/api/v1/contracts/{contract_id}/status` | Update contract status |

### Payments
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/payments` | Create payment intent (escrow) |
| POST | `/api/v1/payments/{payment_id}/release` | Release funds to freelancer |
| POST | `/api/v1/payments/{payment_id}/refund` | Refund payment |
| POST | `/api/v1/payments/webhook` | Stripe webhook handler |

### Messages
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/messages` | Send message |
| GET | `/api/v1/messages/conversations/{user_id}` | Get conversation history |
| GET | `/api/v1/messages/unread-count` | Get unread message count |

### Notifications
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/notifications` | List notifications (paginated) |
| PATCH | `/api/v1/notifications/{id}/read` | Mark notification as read |

### Reviews
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/reviews/` | Leave review |
| GET | `/api/v1/reviews/user/{user_id}` | Get user reviews |
| GET | `/api/v1/reviews/user/{user_id}/rating` | Get user rating |

### Freelancers
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/freelancers` | Search freelancers (paginated, filterable) |
| GET | `/api/v1/freelancers/{user_id}` | Get public freelancer profile |

### Disputes
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/disputes` | Open dispute on contract |
| PATCH | `/api/v1/disputes/{dispute_id}/resolve` | Resolve dispute (admin) |
| GET | `/api/v1/disputes/admin` | List disputes (admin) |

### Admin
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/admin/users` | List all users (admin) |
| PATCH | `/api/v1/admin/users/{user_id}/ban` | Ban user |
| PATCH | `/api/v1/admin/users/{user_id}/unban` | Unban user |
| GET | `/api/v1/admin/jobs` | List all jobs (admin) |
| DELETE | `/api/v1/admin/jobs/{job_id}` | Delete job (moderation) |
| GET | `/api/v1/admin/stats` | Platform statistics |

### Real-time
| Method | Endpoint | Description |
|---|---|---|
| WS | `/api/v1/ws/{user_id}?token=...` | WebSocket — notifications + chat |

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

| Service | URL |
|---|---|
| API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| Flower (Celery) | http://localhost:5555 |
| MailHog (email) | http://localhost:8025 |
| MinIO (storage) | http://localhost:9001 |

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

**264 tests** — unit + integration, **92%+ coverage**

---

## 📄 Environment Variables

````env
# App
APP_ENV=development
DEBUG=True

# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5433/freelance_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=freelance_db

# Redis
REDIS_URL=redis://localhost:6380
CELERY_BROKER_URL=redis://localhost:6380/1

# Auth
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
ALLOWED_ORIGINS=["http://localhost:3000"]

# Mail
MAIL_HOST=localhost
MAIL_PORT=1025
MAIL_FROM=noreply@freelance.com

# Stripe
STRIPE_SECRET_KEY=sk_test_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_secret_here

# MinIO / S3
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
AWS_REGION=us-east-1
S3_BUCKET=freelance-platform
S3_ENDPOINT_URL=http://localhost:9000
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
```
---

## 👤 Author

**Muhammet Myratgeldiyev**

- GitHub: [@myratgeldiyevm1112](https://github.com/myratgeldiyevm1112)
- LinkedIn: [Muhammet Myratgeldiyev](https://www.linkedin.com/in/muhammet-myratgeldiyev-aa8736413)

---

## 📝 License

MIT