# COMPLETE PROJECT CONTEXT
# Everything Prism needs to know about this project

---

## 1. Module & Submission

- **Module:** COMP3011 Web Services and Web Data
- **University:** University of Leeds, UK
- **Student:** Ali
- **Submission deadline:** 13 March 2026 (report to Minerva, code to GitHub)
- **Oral exam:** Week of 23–27 March 2026
- **GitHub:** https://github.com/9ali-oop/hotel-booking-api

---

## 2. Project Overview

The Hotel Booking Intelligence API is a fully-featured RESTful web service built with Python and FastAPI. It ingests and serves the Kaggle Hotel Booking Demand dataset (119,390 records across two Portuguese hotels) and extends it with operational CRUD resources, analytics, intelligent risk scoring, and an AI-powered natural language risk assessment endpoint.

### Problem Domain

Hotel cancellations represent a significant revenue management challenge. The Kaggle dataset (Antonio, Almeida, and Nunes, 2019) documents that cancellation rates can exceed 40% in some properties, costing the European hotel industry billions annually. This API enables hotel operations staff to:

- Explore the dataset programmatically
- Log and manage operational incidents
- Record manager notes against bookings
- Retrieve analytics on cancellation rates, seasonal demand, and market segment performance
- Identify high-risk bookings using a rule-based scoring heuristic
- Obtain AI-generated natural language risk assessments powered by GPT

### Dataset

- **Source:** Kaggle Hotel Booking Demand (Antonio et al., 2019)
- **Records:** 119,390 booking records
- **Hotels:** City Hotel and Resort Hotel (both in Portugal)
- **Fields include:** hotel type, lead_time, arrival_date, stays_in_weekend_nights, stays_in_week_nights, adults, children, babies, meal, country, market_segment, distribution_channel, is_repeated_guest, previous_cancellations, previous_bookings_not_canceled, reserved_room_type, assigned_room_type, booking_changes, deposit_type, days_in_waiting_list, customer_type, adr (average daily rate), required_car_parking_spaces, total_of_special_requests, reservation_status, is_canceled

---

## 3. Technology Stack

### FastAPI (v0.115+)
- **Why:** FastAPI generates OpenAPI/Swagger documentation automatically from Python type hints, reducing documentation burden. It supports async/await natively, enabling non-blocking I/O for the LLM integration. Pydantic integration provides automatic request validation. Benchmarked faster than Flask and Django REST Framework (Pydantic docs, 2024).
- **Alternative considered:** Flask. Rejected because Flask requires manual OpenAPI documentation and does not natively support async.

### SQLAlchemy 2.0
- **Why:** Industry-standard Python ORM with the new 2.0 declarative API offering cleaner model definitions. Supports multiple database backends — the same models would work against PostgreSQL in production without code changes.
- **Alternative considered:** Tortoise-ORM (async-native). Rejected because SQLAlchemy's maturity, documentation, and community support are superior for coursework maintainability.

### SQLite
- **Why:** Zero-configuration database requiring no server process. The entire database is a single file, enabling immediate `git clone && python run.py` setup. Entirely appropriate for a 119,390-row read-heavy workload.
- **Trade-off acknowledged:** SQLite has write-lock contention under concurrent writes. For a production hotel system, PostgreSQL would be used. This limitation is documented.

### Pydantic v2
- **Why:** Integrated with FastAPI for automatic request body parsing, type coercion, and validation. Provides 422 Unprocessable Entity responses with field-level error detail automatically.

### PyJWT (>=2.10.1)
- **Why:** Pure-Python JWT library with no external C dependencies, making it portable across environments. Implements RFC 7519 (JSON Web Tokens). The `>=2.10.1` lower bound was required due to a version conflict with the `mcp` dependency.

### httpx (AsyncClient)
- **Why:** Modern async-first HTTP client. Used for the OpenAI API call. Unlike `requests` (which blocks the event loop), `httpx.AsyncClient` yields control while awaiting the LLM response, keeping other endpoints responsive.

### slowapi
- **Why:** Rate limiting middleware for FastAPI/Starlette. Configured at 60 requests/minute globally. Protects against denial-of-service and API abuse without requiring a separate proxy layer.

### pytest + httpx (TestClient)
- **Why:** pytest is the de facto Python testing framework. FastAPI's `TestClient` wraps the ASGI app directly, enabling integration tests without a running server. Using SQLAlchemy's `StaticPool` with an in-memory SQLite database for each test session ensures full isolation and repeatability.

### fastapi-mcp
- **Why:** Implements the Model Context Protocol (MCP), allowing AI assistants (Claude, GPT) to use the API as a tool. Demonstrates awareness of emerging AI integration standards (Anthropic, 2024).

### GitHub Actions
- **Why:** Native CI/CD integration with GitHub. Matrix strategy tests against Python 3.10, 3.11, and 3.12 simultaneously, catching version-specific regressions. Triggers on both push and pull_request events.

### Railway
- **Why:** Heroku-like PaaS with GitHub integration. Automatically deploys on push to main. Free tier sufficient for demonstration. Procfile-based configuration aligns with 12-factor app principles (Wiggins, 2011).

### Chart.js (frontend)
- **Why:** Lightweight JavaScript charting library loaded via CDN. Provides interactive visualisations in the static dashboard at `/dashboard` without a separate frontend build step.

---

## 4. System Architecture

The application follows a strict layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│  HTTP LAYER                                                   │
│  FastAPI routers, Swagger UI (/docs), CORS middleware,       │
│  slowapi rate limiting (60 req/min), health check (/health)  │
├─────────────────────────────────────────────────────────────┤
│  AUTHENTICATION LAYER                                         │
│  require_api_key() FastAPI dependency                         │
│  Accepts: X-API-Key header OR Authorization: Bearer JWT      │
│  hmac.compare_digest() for timing-safe comparison            │
├─────────────────────────────────────────────────────────────┤
│  SCHEMA LAYER                                                 │
│  Pydantic v2 models — request validation & response shaping  │
│  BookingResponse, IncidentCreate, AIRiskAssessment, etc.     │
├─────────────────────────────────────────────────────────────┤
│  SERVICE LAYER                                                │
│  risk_scoring.py — rule-based heuristic (0.0–1.0 score)      │
│  llm_analysis.py — async OpenAI GPT call + template fallback │
├─────────────────────────────────────────────────────────────┤
│  ORM LAYER                                                    │
│  SQLAlchemy 2.0 declarative models                            │
│  Booking, Incident, ManagerNote with FK relationships         │
├─────────────────────────────────────────────────────────────┤
│  DATABASE LAYER                                               │
│  SQLite — 119,390 bookings + incidents + manager_notes        │
│  In-memory SQLite (StaticPool) used during tests              │
└─────────────────────────────────────────────────────────────┘

Orthogonal concerns:
  GitHub Actions CI  ───→  pytest (3.10/3.11/3.12) ───→  Railway deploy
```

**Dependency injection** is used throughout via FastAPI's `Depends()` mechanism. The database session, authentication check, and other shared resources are injected into route handlers rather than accessed globally, enabling clean unit testing via dependency override.

---

## 5. API Endpoint Catalogue

| Method | Path | Auth Required | Description |
|--------|------|---------------|-------------|
| GET | / | No | Root — project info and links |
| GET | /health | No | Health check (status: ok, version) |
| GET | /bookings | No | List bookings (filter: hotel, country, is_canceled; paginate: skip, limit) |
| GET | /bookings/{id} | No | Get single booking by ID |
| GET | /analytics/cancellation-rate | No | Overall and per-hotel cancellation rates |
| GET | /analytics/monthly-demand | No | Monthly booking volume by year |
| GET | /analytics/market-segment-performance | No | Cancellation rate and ADR by market segment |
| GET | /insights/high-risk-bookings | No | Bookings scored above risk threshold (default 0.6) |
| GET | /insights/operational-hotspots | No | Countries and segments with highest risk concentrations |
| POST | /auth/token | No (uses API key in body) | Exchange API key for JWT Bearer token |
| POST | /incidents | **Yes** | Create incident against a booking |
| GET | /incidents | No | List all incidents (filter by severity, status, booking_id) |
| GET | /incidents/{id} | No | Get single incident |
| PUT | /incidents/{id} | **Yes** | Full update of incident |
| PATCH | /incidents/{id} | **Yes** | Partial update (status only) |
| DELETE | /incidents/{id} | **Yes** | Delete incident |
| POST | /notes | **Yes** | Create manager note against a booking |
| GET | /notes | No | List all notes (filter by booking_id) |
| GET | /notes/{id} | No | Get single note |
| DELETE | /notes/{id} | **Yes** | Delete note |
| POST | /insights/ai-risk-assessment/{booking_id} | **Yes** | AI-powered risk assessment |
| GET | /dashboard | No | Static frontend dashboard |

**Design decisions:**
- Read operations (GET) are public — analytics and data exploration have no sensitive data
- Write operations require authentication — creating/modifying operational records (incidents, notes) should be auditable
- `POST /insights/ai-risk-assessment` requires auth because it invokes a paid external API (OpenAI)
- PATCH on incidents is intentionally limited to `status` field only, following the principle of minimal surface area

---

## 6. Database Schema

### bookings table (119,390 rows, read-only)
Primary key: `id` (auto-increment). All columns from the Kaggle CSV, including: hotel (VARCHAR), lead_time (INT), arrival_date_year (INT), arrival_date_month (VARCHAR), arrival_date_day_of_month (INT), stays_in_weekend_nights (INT), stays_in_week_nights (INT), adults (INT), children (FLOAT), babies (INT), meal (VARCHAR), country (VARCHAR), market_segment (VARCHAR), distribution_channel (VARCHAR), is_repeated_guest (INT), previous_cancellations (INT), previous_bookings_not_canceled (INT), reserved_room_type (VARCHAR), assigned_room_type (VARCHAR), booking_changes (INT), deposit_type (VARCHAR), days_in_waiting_list (INT), customer_type (VARCHAR), adr (FLOAT), required_car_parking_spaces (INT), total_of_special_requests (INT), reservation_status (VARCHAR), reservation_status_date (VARCHAR), is_canceled (INT).

### incidents table
Fields: id (PK), booking_id (FK → bookings.id, CASCADE DELETE), incident_type (VARCHAR, enum: maintenance/billing/complaint/other), severity (VARCHAR, enum: low/medium/high/critical), status (VARCHAR, enum: open/in_progress/resolved), description (TEXT, min 10 chars), reported_by (VARCHAR), created_at (DATETIME), updated_at (DATETIME).

### manager_notes table
Fields: id (PK), booking_id (FK → bookings.id, CASCADE DELETE), note_text (TEXT, min 1 char), author (VARCHAR), created_at (DATETIME).

**Denormalisation decision:** The bookings table is intentionally denormalised (e.g., hotel name stored as a string rather than a foreign key to a hotels table). This faithfully mirrors the dataset structure and reduces query complexity for a read-heavy analytics API.

---

## 7. Authentication System

### API Key
- Configured via `API_KEY` environment variable (default: `hotel-booking-dev-key-2025` for development)
- Submitted as `X-API-Key` HTTP header
- Validated using `hmac.compare_digest()` — this prevents timing attacks where an attacker could determine the correct key character-by-character by measuring response time. Standard string comparison (`==`) is vulnerable; HMAC comparison takes constant time regardless of where the strings diverge.

### JWT Bearer Token
- Client calls `POST /auth/token` with a valid API key in the request body
- Server generates a JWT signed with HS256 using a secret derived from the API key via SHA-256
- Token payload includes standard claims: `sub` (subject), `iss` (issuer: "hotel-booking-api"), `iat` (issued at), `exp` (expiry: 30 minutes)
- Client submits subsequent requests with `Authorization: Bearer <token>`
- Stateless — no server-side session storage required
- Implements RFC 7519 (Jones et al., 2015)

### FastAPI Dependency Injection
```python
async def require_api_key(
    api_key: Optional[str] = Security(api_key_header),
    bearer: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
) -> str:
```
Both authentication methods are tried in the same dependency. If neither is provided → 401 Unauthorized. If provided but invalid → 403 Forbidden. This distinction is important: 401 means "you haven't told us who you are," 403 means "we know who you are but you're not allowed."

---

## 8. Risk Scoring Engine

File: `app/services/risk_scoring.py`

The engine assigns a cancellation risk score between 0.0 and 1.0 based on domain-informed heuristics derived from the Antonio et al. (2019) research findings:

| Factor | Weight | Justification |
|--------|--------|---------------|
| Lead time 100–200 days | +0.15 | Longer lead times correlate with higher cancellation rates (Antonio et al., 2019) |
| Lead time > 200 days | +0.25 | Extreme lead times show even higher cancellation probability |
| 1 previous cancellation | +0.20 | Historical cancellation behaviour is a strong predictor |
| 2+ previous cancellations | +0.30 | Repeated cancellers show significantly higher probability |
| No deposit | +0.15 | No-deposit bookings have lower commitment |
| Online Travel Agent segment | +0.10 | OTA bookings correlate with higher cancellations |
| First-time guest | +0.10 | Repeat guests tend to cancel less |
| Zero booking changes | +0.10 | Modified bookings indicate active engagement |

**Score bands:** LOW < 0.3, MEDIUM 0.3–0.6, HIGH > 0.6. Configurable threshold via `?min_risk` query parameter.

---

## 9. AI-Powered Risk Assessment

Endpoint: `POST /insights/ai-risk-assessment/{booking_id}`

### Pipeline

1. **Fetch:** Retrieve full booking record from database
2. **Score:** Run rule-based risk engine → produces (score: float, band: str, factors: list[str])
3. **Construct prompt:** Build a structured message with booking context, risk score, and contributing factors
4. **LLM call:** Async POST to OpenAI Chat Completions API (`gpt-3.5-turbo` by default, configurable via `OPENAI_MODEL` env var)
5. **Return:** Structured JSON response with booking_id, hotel, risk_score, risk_band, risk_factors, ai_assessment (narrative), ai_model, ai_source

### System Prompt Design
The system prompt instructs GPT to act as "a senior hotel revenue management analyst." Temperature is set to 0.3 (favouring consistency over creativity) and max_tokens to 400 (balancing richness with cost). The prompt structure enforces a four-section output: Risk Summary, Key Risk Factors, Recommended Actions, Revenue Impact.

### Graceful Degradation
If `OPENAI_API_KEY` is not set (e.g., in CI/CD, during testing, or in development), the service falls back to a deterministic template that populates the same response schema from the rule-based factors. This ensures:
- All 58 tests pass without any API calls or mocking
- The endpoint remains functional in all environments
- The response schema is identical regardless of whether GPT was used

### Ethical Considerations
The LLM is used as an advisory tool, not a decision-making system. Its output is labelled as AI-generated, includes the model name and source, and is one input among several for hotel staff. The system does not autonomously cancel bookings or penalise guests based on AI output.

---

## 10. Testing Strategy

**Total: 58 automated tests** across 6 modules.

| Module | Tests | Coverage |
|--------|-------|----------|
| test_bookings.py | 7 | Listing with filters, pagination, 404 |
| test_incidents.py | 16 | Full CRUD lifecycle, 401/403, validation (422), not-found (404) |
| test_notes.py | 11 | CRUD operations, auth enforcement, edge cases |
| test_analytics.py | 8 | Cancellation rate, monthly demand, segments, root, health |
| test_auth.py | 9 | API key valid/invalid, JWT obtain/use/invalid, public endpoints |
| test_ai_insights.py | 7 | Response schema, 404, 401, 403, template fallback, risk scoring |

**Test infrastructure:**
- `StaticPool` + in-memory SQLite: each test session gets a fresh, isolated database — no test pollution
- FastAPI `TestClient` wraps the ASGI app directly — no running server needed
- `conftest.py` provides shared fixtures: database session, test client, sample booking data
- GitHub Actions matrix (Python 3.10, 3.11, 3.12) catches version-specific regressions
- Tests run in 0.87 seconds — fast enough to run on every commit

**Test categories covered:**
- Happy path (2xx responses)
- Validation errors (422 Unprocessable Entity)
- Authentication failures (401 Unauthorized, 403 Forbidden)
- Not-found errors (404)
- Edge cases (empty results, min/max values, duplicate prevention)

---

## 11. Deployment

### Railway (Production)
- **Platform:** Railway.app (PaaS)
- **Live base URL:** https://web-production-c9799.up.railway.app/
- **Interactive API docs (Swagger UI):** https://web-production-c9799.up.railway.app/docs
- **Live Intelligence Dashboard:** https://web-production-c9799.up.railway.app/dashboard
- **Configuration:** `Procfile` (`web: uvicorn run:app --host 0.0.0.0 --port $PORT`), `runtime.txt` (python-3.10.12), `railway.toml`
- **Environment variables:** `API_KEY`, `OPENAI_API_KEY` (optional), `PORT` (auto-set by Railway)
- **Health check:** `GET /health` returns `{"status": "ok", "version": "1.0.0"}`
- **Deploy trigger:** Auto-deploys from the `main` branch on push

### Frontend Dashboard
- **Served at:** `/dashboard` — FastAPI serves `static/index.html` via `FileResponse`
- **Tech:** Single-page vanilla HTML/JS with Chart.js for visualisations; no framework dependency
- **Tabs:** Overview (KPI cards + monthly demand + market segment charts), Bookings (paginated/filtered table), Incidents (CRUD), Notes (CRUD), Analytics (cancellation rate + ADR charts), Risk Analysis (AI Insights)
- **Risk Analysis tab features:** Filterable high-risk booking table with adjustable threshold slider; per-row "✨ Analyse" button that calls `POST /insights/ai-risk-assessment/{id}` with API key auth and renders the GPT-generated narrative inline as an expandable panel beneath each row
- **AI feature UX:** API key entered once in a secure password field at top of Risk tab; result shows risk band, model used (GPT or fallback), and full LLM narrative; toggle to hide/show

### GitHub Actions CI
- **Trigger:** Push to any branch, pull request to main
- **Matrix:** Python 3.10, 3.11, 3.12
- **Steps:** Checkout → Set up Python → Install dependencies (`pip install -r requirements.txt`) → Run tests (`pytest tests/ -v`)
- **Effect:** Prevents any failing commit from reaching main

### 12-Factor App Alignment (Wiggins, 2011)
- Config via environment variables (not hardcoded)
- Stateless process (no local session state)
- Port binding via `$PORT`
- Dev/prod parity (same codebase, different env vars)
- Disposability (fast startup, graceful shutdown)

---

## 12. Challenges and Solutions

### Challenge 1: PyJWT Version Conflict
**Problem:** Installing `PyJWT==2.9.0` caused a dependency conflict with the `mcp` package which required `PyJWT>=2.10.1`. pip resolved this silently, leading to an import error at runtime.
**Solution:** Set the requirements.txt pin to `PyJWT>=2.10.1` (a lower bound rather than an exact version), allowing pip to install the latest compatible version. Lesson: over-pinning dependencies causes fragility; use lower bounds for libraries with stable APIs.

### Challenge 2: Test Isolation with Async LLM Calls
**Problem:** The `ai-risk-assessment` endpoint makes async HTTP calls to OpenAI. Tests would fail without a real API key, and mocking async clients in pytest requires careful fixture design.
**Solution:** Implemented graceful degradation at the service layer (template fallback when `OPENAI_API_KEY` is absent), eliminating the need for mocking entirely. Tests verify the template fallback produces the correct schema. This is architecturally cleaner than test mocking and provides better production resilience.

### Challenge 3: Timing-Safe Authentication
**Problem:** Standard string comparison (`api_key == API_KEY`) is vulnerable to timing attacks — an attacker can determine the correct key one character at a time by measuring microsecond differences in comparison time.
**Solution:** Used `hmac.compare_digest()` from Python's standard library, which performs a constant-time comparison regardless of where the strings diverge. This is a straightforward security hardening measure aligned with OWASP API Security Top 10 (OWASP Foundation, 2023).

### Challenge 4: Stateless JWT with Refresh Considerations
**Problem:** JWTs are stateless — there is no server-side revocation mechanism. A stolen token is valid until expiry.
**Solution:** Set a short expiry (30 minutes) to limit the window of exposure. Acknowledged as a known limitation in the evaluation section; a production system would implement refresh token rotation and a token revocation list (e.g., Redis-backed blocklist).

---

## 13. Limitations and Future Work

- **SQLite concurrency:** SQLite's write-lock would be a bottleneck under concurrent write load. Production deployment should use PostgreSQL with connection pooling (e.g., PgBouncer).
- **JWT revocation:** No token blacklist implemented. Adding Redis-backed revocation would address this.
- **Risk scoring accuracy:** The heuristic is based on domain knowledge rather than trained machine learning. A logistic regression or gradient-boosted model trained on the dataset would produce higher predictive accuracy.
- **No OAuth2:** The authentication does not implement the full OAuth2 specification. Adding OAuth2 with scopes would enable fine-grained permission management.
- **Static dashboard:** The Chart.js frontend serves pre-aggregated data from the API. A real-time dashboard would use WebSockets.
- **LLM cost and latency:** Each AI risk assessment call adds ~1–3 seconds of latency and consumes OpenAI API credits. Caching frequent assessments would reduce both.

---

## 14. Generative AI Usage Declaration

The following AI tools were used during this project:

1. **Claude (Anthropic)** — used as an AI coding assistant via Claude Code and the Cowork desktop application throughout development. Assisted with: initial architecture design, boilerplate generation for FastAPI routes and SQLAlchemy models, test suite scaffolding, authentication implementation (API Key + JWT), LLM integration service design, documentation generation (README, technical report, presentation), and debugging. All AI-generated code was reviewed, understood, and deliberately integrated by the student. The design decisions, architecture choices, and learning outcomes are the student's own.

2. **ChatGPT (OpenAI GPT-5.2 / Prism)** — used for drafting and refining this technical report. The student provided full project context and iteratively reviewed and revised the output to ensure accuracy and alignment with the implemented system.

3. **OpenAI GPT (via API)** — integrated directly into the Hotel Booking Intelligence API itself as the `ai-risk-assessment` endpoint. This represents a deliberate, assessed application of generative AI to the project's core functionality.

Conversation logs documenting AI-assisted development are included in `docs/genai_conversation_logs/`.

---

## 15. Key Numbers (for the report)

- 119,390 booking records
- 20+ API endpoints
- 58 automated tests (all passing)
- 0.87 seconds to run the full test suite
- 6 test modules
- 2 authentication methods (API Key + JWT)
- 3 database tables
- Python 3.10 / 3.11 / 3.12 tested
- 30-minute JWT expiry
- 60 requests/minute rate limit
- Temperature 0.3, max 400 tokens for LLM calls
- 5 CI/CD steps per workflow run
