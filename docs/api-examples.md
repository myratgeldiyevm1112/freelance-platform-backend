# API Examples

## Auth

### Register
```bash
curl -X POST https://freelance-platform-backend-gkyj.onrender.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "client@example.com",
    "password": "password123",
    "full_name": "Ali Client",
    "role": "client"
  }'
```

### Login
```bash
curl -X POST https://freelance-platform-backend-gkyj.onrender.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "client@example.com",
    "password": "password123"
  }'
```

## Jobs

### Create job
```bash
curl -X POST https://freelance-platform-backend-gkyj.onrender.com/api/v1/jobs/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Build a REST API",
    "description": "Need a FastAPI developer for a freelance platform project",
    "budget": 500
  }'
```

### List jobs (with pagination)
```bash
curl "https://freelance-platform-backend-gkyj.onrender.com/api/v1/jobs/?page=1&page_size=10&status=open" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Proposals

### Submit proposal
```bash
curl -X POST https://freelance-platform-backend-gkyj.onrender.com/api/v1/proposals/jobs/JOB_ID/proposals \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cover_letter": "I have 3 years of FastAPI experience and can deliver quality work",
    "proposed_rate": 450
  }'
```

### Accept proposal
```bash
curl -X PATCH https://freelance-platform-backend-gkyj.onrender.com/api/v1/proposals/PROPOSAL_ID \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "accepted"}'
```

## Contracts

### Complete contract
```bash
curl -X PATCH https://freelance-platform-backend-gkyj.onrender.com/api/v1/contracts/CONTRACT_ID/status \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"new_status": "completed"}'
```

## Reviews

### Leave review
```bash
curl -X POST https://freelance-platform-backend-gkyj.onrender.com/api/v1/reviews/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contract_id": "CONTRACT_ID",
    "rating": 5,
    "comment": "Great work, very professional!"
  }'
```

### Get user rating
```bash
curl https://freelance-platform-backend-gkyj.onrender.com/api/v1/reviews/user/USER_ID/rating \
  -H "Authorization: Bearer YOUR_TOKEN"
```
