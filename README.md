# Smith Point Capital — Relationship Connectivity Platform

A relationship intelligence tool for Smith Point Capital. Scores connections between the SP team and any company's leadership across employment history, education, board seats, location, and prior interactions.

## Repository Structure

```
├── frontend/          # Static React app — deployed via GitHub Pages
│   ├── index.html     # Main app (self-contained React + Babel)
│   └── config.js      # ← Edit this to point at your backend URL
│
├── backend/           # FastAPI Python API
│   ├── main.py        # All endpoints
│   ├── models.py      # SQLAlchemy schema
│   ├── scoring.py     # Connectivity scoring engine
│   ├── seed.py        # SP team seed data (10 members, verified LinkedIn URLs)
│   ├── schemas.py     # Pydantic request/response models
│   ├── database.py    # DB connection (SQLite dev / Postgres prod)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
│
└── .github/workflows/
    └── deploy.yml     # Auto-deploys frontend to GitHub Pages on push to main
```

## Quick Start

### 1. Frontend (GitHub Pages — free)

1. Push this repo to GitHub
2. Go to **Settings → Pages → Source → GitHub Actions**
3. Push to `main` — the workflow deploys automatically
4. Your app is live at `https://<your-username>.github.io/<repo-name>/`

### 2. Backend (optional — needed for live database)

**Local development:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
# API at http://localhost:8000
# Docs at http://localhost:8000/docs
```

**Docker (local Postgres):**
```bash
cd backend
docker compose up -d
```

**Deploy to Fly.io (recommended for production):**
```bash
cd backend
fly launch          # follow prompts, select a region
fly secrets set DATABASE_URL=postgresql://...
fly deploy
# API live at https://your-app.fly.dev
```

### 3. Connect Frontend to Backend

After deploying the backend, edit `frontend/config.js`:

```js
window.RCP_API_BASE = "https://your-app.fly.dev";
```

Commit and push — the GitHub Actions workflow redeploys in ~30 seconds.

## Scoring Signals

| Signal | Points | Logic |
|--------|--------|-------|
| Company overlap | up to 30 | Scaled by years of overlap + recency decay |
| Board seat overlap | 20 | Flat |
| Education (same years) | 20 | Same school, overlapping graduation years |
| Education (different years) | 12 | Same school, different years |
| Location | 5 | Same city |
| Prior interaction | up to 25 | Decays exponentially by months since contact |

**Strength thresholds:** Strong ≥ 40 · Medium ≥ 20 · Weak < 20

## Team Data

10 SP team members are auto-seeded on first backend startup with verified LinkedIn URLs (Feb 2026) and corrected education data:
- Keith Block, Burke Norton, Christopher Lytle, John Cummings, Tyler Prince
- Brooke Kiley Slattery, Lorenzo Salazar, Sewon Park, Katie Rodday, Lilly Cordover
