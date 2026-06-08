# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.2.0] - 2025-06-08

### Added

#### 💬 Messaging (Real-time Chat)
- `Message` model with sender, receiver, job/contract association, `is_read` flag and timestamp
- Alembic migration for messages table
- `MessageRepository` with `get_by_conversation` and `mark_as_read` methods
- `SendMessage` and `GetMessages` use cases
- REST endpoints: `POST /api/v1/messages`, `GET /api/v1/messages/conversations/{user_id}`
- Unread message count endpoint: `GET /api/v1/messages/unread-count`
- WebSocket real-time chat — messages pushed instantly via existing WebSocket manager
- Full test coverage for messaging flow

#### 💳 Payments (Stripe Escrow)
- `Payment` model with escrow statuses (`pending`, `held`, `released`, `refunded`)
- Alembic migration for payments table
- Stripe SDK integration — `PaymentIntent`, `Transfer`, `Refund`
- Escrow flow: client pays on proposal acceptance, funds held until contract completion
- `POST /api/v1/payments` — create payment intent
- `POST /api/v1/payments/{payment_id}/release` — release funds to freelancer
- `POST /api/v1/payments/{payment_id}/refund` — refund on contract cancellation
- Platform commission (10%) automatically withheld on release
- Stripe webhook handling: `payment_intent.succeeded`, `payment_intent.payment_failed`
- Tests with Stripe mocks

#### 🔔 Notifications Center
- `Notification` model (`user_id`, `type`, `message`, `is_read`, `created_at`)
- `NotificationRepository` + use cases (`get_notifications`, `mark_as_read`)
- `GET /api/v1/notifications` — paginated notifications list
- `PATCH /api/v1/notifications/{id}/read` — mark single notification as read
- Integrated into all platform events: proposal submitted/accepted, contract updates, new message, payment events
- WebSocket push on new notification — real-time delivery
- Full test coverage

### Stats
- **105 tests** — unit + integration
- **Coverage: 85%+**

---

## [1.1.0] - 2025-05-15

### Added

#### 🛠 Skills
- `Skill` model and many-to-many `UserSkill` relation
- `POST /api/v1/users/me/skills` — add skills to profile
- `GET /api/v1/users/me/skills` — list my skills
- `DELETE /api/v1/users/me/skills/{skill_id}` — remove skill
- Job filtering by required skill

#### 🔍 Job Search
- Full-text search by title and description using PostgreSQL `tsvector`
- `search_vector` column with GIN index for fast queries
- Filter jobs by `status`, `budget_min/max`, `skill`

#### 📁 File Upload
- Avatar upload: `POST /api/v1/users/me/avatar` (JPG/PNG, max 5MB)
- Portfolio upload: `POST /api/v1/users/me/portfolio` (JPG/PNG/PDF, max 5MB)
- Files stored in AWS S3 / MinIO, URL persisted to user profile
- `avatar_url` and `portfolio_urls` fields on `UserEntity` and DTO

#### ⚡ Real-time WebSockets
- WebSocket endpoint: `WS /api/v1/ws/{user_id}?token=...`
- JWT authentication on handshake
- Real-time push: `proposal_submitted`, `proposal_accepted`
- Multiple concurrent connections per user supported

#### 🚦 Rate Limiting
- SlowAPI integration
- Register: 5 requests/min
- Login: 10 requests/min

#### 🗂 Caching (Redis)
- Jobs list cached with 60s TTL, invalidated on create/update
- User rating cached with 5min TTL

#### 🔐 Auth Improvements
- Refresh tokens stored in Redis
- `POST /api/v1/auth/logout` — invalidates refresh token

#### ⚙️ Infrastructure
- Celery + Redis broker for background tasks
- Email notifications via Celery (proposal accepted, contract completed)
- Flower (Celery monitor) added to Docker Compose
- MailHog (email preview) added to Docker Compose
- MinIO (local S3) added to Docker Compose
- Lazy S3 client init — CI works without MinIO

### Stats
- **84 tests** — unit + integration
- **Coverage: 83%**

---

## [1.0.0] - 2025-04-20

### Added

#### 🔑 Auth
- User registration with `client` / `freelancer` roles
- Login with JWT access + refresh tokens
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`

#### 👤 Users
- `GET /api/v1/users/me` — get profile
- `PATCH /api/v1/users/me` — update profile

#### 💼 Jobs
- Create, list, filter and paginate job postings
- `POST /api/v1/jobs/`
- `GET /api/v1/jobs/` — with `status`, `budget` filters and pagination
- `GET /api/v1/jobs/{job_id}`

#### 📋 Proposals
- Submit proposals (freelancers only)
- Accept / reject proposals (clients only)
- Duplicate proposal prevention
- Auto-create contract on accept
- `POST /api/v1/proposals/jobs/{job_id}/proposals`
- `GET /api/v1/proposals/jobs/{job_id}/proposals`
- `PATCH /api/v1/proposals/{proposal_id}`

#### 📄 Contracts
- Contract lifecycle: `active` → `completed` / `cancelled`
- `GET /api/v1/contracts/{contract_id}`
- `PATCH /api/v1/contracts/{contract_id}/status`

#### ⭐ Reviews
- Leave reviews after contract completion (1–5 stars)
- Average rating aggregation
- `POST /api/v1/reviews/`
- `GET /api/v1/reviews/user/{user_id}`
- `GET /api/v1/reviews/user/{user_id}/rating`

#### 🏗 Infrastructure
- Clean Architecture: `api` → `application` → `domain` ← `infrastructure`
- PostgreSQL + SQLAlchemy async
- Alembic migrations
- Docker + Docker Compose
- GitHub Actions CI
- Render deployment (`render.yaml`)
- Ruff linter
- Pydantic v2 validation
- Centralized error handling with custom domain exceptions
- Structured logging + request middleware

### Stats
- **48 tests** — unit + integration
- **Coverage: 86%**
