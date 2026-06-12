# KSP Crime Intelligence Platform — Backend

AI-powered Crime Intelligence Platform for the Karnataka State Police Datathon 2025.

## Architecture

```
FastAPI Backend
├── PostgreSQL (Crime records, users, audit)
├── Neo4j (Criminal network graph)
├── ChromaDB (Vector search, conversation memory)
├── Redis (Caching, sessions)
└── Gemini AI (Conversational intelligence)
```

## Quick Start

### 1. Start Infrastructure (Docker)

```bash
cd docker
docker-compose up -d
```

This starts PostgreSQL, Neo4j, Redis, and ChromaDB.

### 2. Install Python Dependencies

```bash
python -m venv venv
.\venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

### 3. Seed Database

```bash
python -m scripts.seed_synthetic
python -m scripts.seed_neo4j     # Optional: populate Neo4j graph
```

### 4. Run Backend

```bash
uvicorn app.main:app --reload --port 8000
```

### 5. Access

- **API Docs (Swagger):** http://localhost:8000/docs
- **API Docs (ReDoc):** http://localhost:8000/redoc
- **Neo4j Browser:** http://localhost:7474
- **Health Check:** http://localhost:8000/health

## Demo Credentials

| Username | Password | Role |
|---|---|---|
| admin | admin123 | Administrator |
| investigator | invest123 | Investigator |
| analyst | analyst123 | Analyst |
| supervisor | super123 | Supervisor |
| policymaker | policy123 | Policymaker |

## API Endpoints

| Module | Prefix | Description |
|---|---|---|
| Auth | `/api/v1/auth` | Login, register, JWT tokens |
| Chat | `/api/v1/chat` | Gemini AI conversational queries |
| FIR | `/api/v1/fir` | CRUD for First Information Reports |
| Accused | `/api/v1/accused` | Accused/suspect management |
| Dashboard | `/api/v1/dashboard` | KPIs, trends, rankings |
| Analytics | `/api/v1/analytics` | Patterns, hotspots, anomalies |
| Networks | `/api/v1/networks` | Criminal network graph |
| Profiles | `/api/v1/profiles` | Offender profiling & risk |
| Forecast | `/api/v1/forecast` | Crime predictions |
| Financial | `/api/v1/financial` | Financial crime analysis |
| Investigation | `/api/v1/investigation` | Case summaries, suggestions |
| Alerts | `/api/v1/alerts` | System alerts |
| Audit | `/api/v1/audit` | Activity audit trail |

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Key variables:
- `DATABASE_URL` — PostgreSQL connection string
- `NEO4J_URI` — Neo4j bolt URL
- `GEMINI_API_KEY` — Google Gemini API key
- `SECRET_KEY` — JWT signing key

## Frontend Integration

The frontend API client is at `src/api/`:

```typescript
import { chatApi, dashboardApi } from '@/api';

// Send a chat message
const response = await chatApi.send({
  content: "Show crime stats for Bengaluru",
  language: "EN"
});

// Get dashboard data
const dashboard = await dashboardApi.getDashboard();
```
