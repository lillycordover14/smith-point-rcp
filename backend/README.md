# Smith Point RCP — Backend API

FastAPI + SQLAlchemy backend for the Relationship Connectivity Platform.

## Stack
- **FastAPI** — REST API
- **SQLAlchemy** — ORM
- **SQLite** (dev) / **PostgreSQL** (prod)
- **Scoring engine** — pure Python, swappable

## Quick Start (local SQLite — no setup needed)

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

API runs at http://localhost:8000  
Interactive docs at http://localhost:8000/docs

## Production (PostgreSQL via Docker)

```bash
docker compose up -d
```

Set `DATABASE_URL=postgresql://rcp:rcp_dev_password@localhost:5432/rcp` in your environment.

## Key Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/people?internal_only=true` | List SP team |
| GET | `/api/people/{id}` | Person detail with roles + education |
| POST | `/api/people` | Add new person |
| GET | `/api/orgs` | List organizations |
| POST | `/api/orgs` | Add organization |
| GET | `/api/connectivity?target_id={id}` | Score one target against all SP members |
| GET | `/api/connectivity/company?linkedin_slug={slug}` | Score all people at a company |
| POST | `/api/roles` | Add work history entry |
| POST | `/api/education` | Add education entry |
| POST | `/api/interactions` | Log a meeting/email/call |

## Scoring Signals

| Signal | Max Points | Logic |
|--------|-----------|-------|
| Company overlap | 30 | Scaled by years of overlap + recency decay |
| Board seat overlap | 20 | Flat |
| Education (with year overlap) | 20 | Same institution, overlapping years |
| Education (no year overlap) | 12 | Same institution, different years |
| Location | 5 | Same city |
| Prior interaction | 25 | Decays exponentially by months since |

Score thresholds: **Strong** ≥ 40 · **Medium** ≥ 20 · **Weak** < 20

## Seed Data

10 SP team members are auto-seeded on first startup with:
- Verified LinkedIn URLs (Feb 2026)
- Corrected education data from LinkedIn profiles
  - Christopher Lytle → Lafayette College (not Dartmouth)
  - Tyler Prince → U of Illinois (not Duke)
  - Brooke Kiley Slattery → Wharton/UPenn (not Harvard)
  - Burke Norton → UC Berkeley Law (not Harvard Law)
  - Lilly Cordover → UVA McIntire (not UPenn)

## Adding Real Company Data

```bash
# 1. Create the org
curl -X POST http://localhost:8000/api/orgs \
  -H "Content-Type: application/json" \
  -d '{"name": "Acme Corp", "linkedin_slug": "acme-corp"}'

# 2. Add a person
curl -X POST http://localhost:8000/api/people \
  -H "Content-Type: application/json" \
  -d '{"full_name": "Jane Doe", "linkedin_url": "...", "is_internal": false}'

# 3. Link them
curl -X POST http://localhost:8000/api/roles \
  -H "Content-Type: application/json" \
  -d '{"person_id": 16, "org_name": "Acme Corp", "title": "CEO", "start_year": 2020}'

# 4. Get connectivity
curl "http://localhost:8000/api/connectivity?target_id=16"
```

## Deployment

### Fly.io (recommended)
```bash
fly launch
fly secrets set DATABASE_URL=postgresql://...
fly deploy
```

### Environment Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./rcp.db` | Database connection string |
