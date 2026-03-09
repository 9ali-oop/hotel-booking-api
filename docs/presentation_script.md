# Presentation Script — Hotel Booking Intelligence API

**Total time: ~8–10 minutes** (aim for 8, leaves buffer for demo)

---

## SLIDE 1 — Title Slide

> "Hi, I'm Ali. My project is the Hotel Booking Intelligence API — a data-driven, AI-powered RESTful API built for hotel operational analytics. I'll walk you through what it does, how it's built, and why I made the design choices I did."

*~15 seconds — click to next slide*

---

## SLIDE 2 — Project Overview

> "So at a high level — the API sits on top of the Kaggle Hotel Booking Demand dataset. That's 119,390 real booking records from two Portuguese hotels, covering 2015 to 2017. Each record has 32 features like lead time, country, market segment, deposit type, and whether it was cancelled.
>
> The API exposes over 20 RESTful endpoints. It has 58 automated tests. And — this is the part I'm most proud of — it integrates OpenAI's GPT at runtime to generate AI-powered risk assessments. So the API itself is AI-powered, not just AI-built.
>
> Key features: full CRUD for incident reports and manager notes, analytics endpoints for cancellation rates and demand trends, a rule-based risk scoring engine, dual authentication with API keys and JWT tokens, rate limiting, and a live interactive dashboard."

*~45 seconds — click to next slide*

---

## SLIDE 3 — Technology Stack

> "For the tech stack — I chose **FastAPI** as the framework because it auto-generates Swagger documentation from Python type hints, has built-in request validation through Pydantic, and supports async natively — which I needed for the non-blocking OpenAI API calls.
>
> **SQLAlchemy 2.0** as the ORM — it's database-agnostic, so I can swap SQLite for PostgreSQL by changing one URL string. **SQLite** for the database itself — zero-config means the examiner can clone and run the project instantly without installing a database server. The trade-off is limited write concurrency, but for a read-heavy API over 119K records, it's ideal.
>
> **PyJWT** for RFC 7519 compliant tokens, **slowapi** for rate limiting at 60 requests per minute, **httpx** for async HTTP calls to OpenAI, and **pytest** with an in-memory SQLite database for fast, isolated testing. GitHub Actions runs the test suite across Python 3.10, 3.11, and 3.12."

*~50 seconds — click to next slide*

---

## SLIDE 4 — Layered Architecture

> "The system follows a layered architecture. Requests come in at the HTTP layer — that's FastAPI handling routing, Swagger UI, CORS, and rate limiting.
>
> Then the Authentication layer — dual auth via API key or JWT Bearer token. Below that, Pydantic schemas validate the input and serialise the output.
>
> The Services layer is where the interesting logic lives — the risk scoring engine and the LLM analysis service. Then the ORM layer maps Python objects to SQL tables, and at the bottom is the SQLite database.
>
> The key pattern here is **dependency injection** via FastAPI's `Depends()`. Every route that needs database access declares `Depends(get_db)` — it gets a fresh session, and it's automatically closed after the request. For testing, I override this dependency to use an in-memory database. That's how each test gets a clean, isolated database in milliseconds."

*~50 seconds — click to next slide*

---

## SLIDE 5 — API Endpoints

> "The API has six resource groups. **Data exploration** — browse and filter bookings with pagination. **Incidents** — full CRUD with POST, GET, PUT, PATCH, and DELETE. **Manager Notes** — a secondary CRUD resource showing relational design. **Analytics** — computed statistics like cancellation rates, monthly demand, and market segment performance. **Insights and AI** — the risk scoring engine and the GPT-powered assessments. And **Authentication** — token issuance.
>
> All write endpoints require authentication. All read endpoints are public — the data comes from a published dataset, so keeping GETs open makes it easy to explore and demo. Everything is rate-limited at 60 requests per minute."

*~40 seconds — click to next slide*

---

## SLIDE 6 — Dual Authentication

> "I implemented a dual authentication system. **API key auth** is simple — you send an `X-API-Key` header. The key is verified using `hmac.compare_digest`, which is a constant-time comparison. This prevents timing-based side-channel attacks — normal string comparison leaks information about which characters match based on how fast it returns.
>
> **JWT Bearer tokens** follow RFC 7519. You POST your API key to `/auth/token` and get back a signed token with standard claims — subject, issuer, issued-at, and expiry. Tokens expire after 30 minutes. One clever detail: the JWT secret is derived from the API key via SHA-256 hashing, so if you change the API key, all existing tokens are automatically invalidated.
>
> Both methods are wired through a single FastAPI dependency — `require_api_key` — which tries the API key first, then falls back to checking the Bearer token. 401 if nothing's provided, 403 if the key is wrong."

*~55 seconds — click to next slide*

---

## SLIDE 7 — AI-Powered Risk Assessment

> "This is the centrepiece of the project — the AI integration. It works in four steps.
>
> **Step 1**: fetch the booking from the database. **Step 2**: run it through the rule-based risk scoring engine to get a numerical score and contributing factors. **Step 3**: build a structured prompt with the booking data and risk score, and send it to OpenAI's Chat Completions API. The system prompt frames the LLM as a 'senior hotel revenue management analyst' and enforces a consistent output structure. **Step 4**: return the combined response — structured data plus the AI narrative.
>
> Key design decisions: **Graceful degradation** — if no OpenAI API key is configured, or if the API is down, the endpoint returns a template-based assessment with the identical response schema. The API contract never breaks. **Async HTTP** — using httpx so the LLM call doesn't block other requests. **Temperature 0.3** — low randomness for factual, consistent assessments. **Max 400 tokens** — keeps responses concise and cost-effective.
>
> This is what I mean by 'creative application of GenAI' — the API itself is AI-powered at runtime, not just built with AI tools."

*~1 minute — click to next slide*

---

## SLIDE 8 — Risk Scoring Engine

> "The risk scoring uses a rule-based heuristic with six weighted factors. Lead time over 200 days adds 0.15 to 0.25. Previous cancellations are the strongest predictor — up to 0.30. No deposit, Online TA bookings, first-time guests, and zero booking changes each add 0.10 to 0.15.
>
> Scores are capped at 1.0 and classified into bands: low under 0.3, medium 0.3 to 0.6, high above 0.6. The threshold is configurable via a query parameter.
>
> Why a heuristic instead of machine learning? It's transparent and interpretable. I can explain exactly why a booking scored 0.65 — it had very high lead time, no deposit, and it's a first-time guest. An ML model is a black box. For a viva context, being able to explain the algorithm is more valuable. I do acknowledge ML as a future improvement."

*~45 seconds — click to next slide*

---

## SLIDE 9 — Testing Strategy

> "58 automated tests across 6 modules. The breakdown: 7 for bookings covering filters and pagination, 16 for incidents covering the full CRUD lifecycle plus auth enforcement, 11 for notes, 8 for analytics, 9 for authentication testing both API key and JWT paths, and 7 for AI insights including the template fallback.
>
> The key pattern is test isolation. Each test gets a fresh in-memory SQLite database through FastAPI's `dependency_overrides` mechanism. The entire suite runs in under a second because there's no disk I/O.
>
> Tests cover happy paths, validation errors returning 422, auth failures returning 401 and 403, 404 for missing resources, and edge cases. GitHub Actions runs this on every push across three Python versions."

*~40 seconds — click to next slide*

---

## SLIDE 10 — Deployment & CI/CD

> "The API is deployed live on Railway — a Platform-as-a-Service. Push to main on GitHub, Railway detects it, Nixpacks auto-builds, and it's live with HTTPS. Environment variables are injected at runtime — API key, OpenAI key, JWT secret.
>
> The CI pipeline runs on GitHub Actions, triggered on push and pull request. It tests across Python 3.10, 3.11, and 3.12 in a matrix. Catches regressions before they reach production.
>
> The project also follows Twelve-Factor App principles — one codebase, explicit dependencies in requirements.txt, config via environment variables, and backing services as attached resources."

*~35 seconds — click to next slide*

---

## SLIDE 11 — Version Control & Documentation

> "For version control — feature-branch workflow with descriptive commit messages and pull requests. The .gitignore excludes data files and secrets.
>
> Documentation is multi-layered: auto-generated Swagger UI at `/docs`, the technical report PDF, inline docstrings on every endpoint and function, Pydantic schemas that document every request and response model, and this presentation."

*~20 seconds — click to next slide*

---

## SLIDE 12 — Live Demo

> "Let me show you the live system. I'll quickly walk through six things."

**Demo order (practise this!):**

1. **Swagger UI** — open `/docs`, show the interactive documentation, point out the endpoint grouping
2. **Auth** — click Authorize, enter the API key, show it's unlocked
3. **CRUD** — create an incident via POST, show the 201 response, then GET it back
4. **Analytics** — hit `/analytics/cancellation-rate`, show the computed statistics
5. **AI Assessment** — call POST `/insights/ai-risk-assessment/1`, show the structured + narrative response. Point out the `ai_source` field
6. **Dashboard** — open `/dashboard`, show the charts, click the Analyse button on a high-risk booking

> "So you can see — the API is fully functional, live, and integrates everything from data exploration to AI-powered analysis."

*~2 minutes for demo — click to next slide*

---

## SLIDE 13 — Thank You

> "That's my project. The GitHub repo is at github.com/9ali-oop/hotel-booking-api, and the live API is running on Railway. Happy to answer any questions."

*~10 seconds*

---

## LIKELY Q&A — Quick Answers

### "Why FastAPI over Flask?"
> "Auto-generated Swagger docs from type hints, built-in Pydantic validation, native async for the OpenAI calls. Flask would need extensions for each of these."

### "Why SQLite?"
> "Zero-config — clone and run. Read-heavy workload fits perfectly. Trade-off is write concurrency, which isn't an issue for a single-writer API. Switching to PostgreSQL is a one-line change because of the ORM."

### "Explain constant-time comparison."
> "Normal `==` returns false at the first mismatched character — so comparing 'aaab' takes longer than 'baaa'. An attacker can time responses to guess the key character by character. `hmac.compare_digest` always takes the same time regardless of where they differ."

### "What's the difference between high-risk-bookings and ai-risk-assessment?"
> "High-risk-bookings is a batch scanner — scans all bookings through the heuristic, returns those above a threshold. AI-risk-assessment is a deep-dive on a single booking — combines the heuristic with a GPT narrative that explains WHY and gives actionable recommendations."

### "Why is ai-risk-assessment a POST not GET?"
> "It has a side effect — calls the OpenAI API, which costs money. GET should be safe and idempotent. POST is correct because each call triggers an external paid API call."

### "What are the limitations?"
> "SQLite write concurrency, no OAuth2 scopes or RBAC, heuristic is rule-based not ML-trained, LLM calls are synchronous within a request, and no end-to-end tests."

### "Future work?"
> "PostgreSQL for concurrency, OAuth2 scopes, trained ML classifier, async task queue for LLM calls, WebSocket real-time alerts, and E2E testing."

### "How did you use GenAI?"
> "Three levels. ChatGPT as a development tool for scaffolding and debugging. Prism for drafting the LaTeX report. And GPT-3.5-turbo embedded as a runtime feature of the API itself — the AI risk assessment endpoint. That third level is the creative application."

### "How does graceful degradation work?"
> "The `_template_fallback()` function generates a structured assessment using the same risk factors but without calling OpenAI. The response schema is identical — the `ai_source` field changes from 'openai' to 'template'. The client never sees an error."

### "How do tests isolate the database?"
> "FastAPI's `dependency_overrides` lets you replace `get_db` with a version that returns an in-memory SQLite session. Each test gets a fresh empty database. No disk I/O, entire suite runs in under a second."

### "What's the JWT secret derived from?"
> "SHA-256 hash of the API key. So changing the API key automatically invalidates all existing tokens — neat security property."

### "What's `Depends()` and why is it important?"
> "It's FastAPI's dependency injection. Routes declare what they need — `Depends(get_db)` for database, `Depends(require_api_key)` for auth. FastAPI resolves these at request time. It gives you separation of concerns, testability through overrides, and per-request lifecycle management."

### "What Pydantic features do you use?"
> "Type-safe schemas for every request and response. `model_dump(exclude_unset=True)` for PATCH operations — only updates fields the client actually sent. `ConfigDict(from_attributes=True)` to convert ORM objects to JSON. `Field(ge=1, le=5)` for validation constraints."

### "What's the dataset about?"
> "Antonio et al., 2019. 119,390 hotel booking records from two Portuguese hotels — a city hotel and a resort hotel — from 2015 to 2017. 32 features per record. About 37% of bookings were cancelled, which is what makes the risk scoring meaningful."

### "Explain the middleware stack."
> "Three layers: CORS middleware allows cross-origin requests from the dashboard. SlowAPI middleware enforces the 60 requests/minute rate limit per IP. And a custom logging middleware records method, path, status code, and latency for every request."

### "What status codes does the API return?"
> "200 for successful reads, 201 for created resources, 400 for bad requests, 401 for missing authentication, 403 for invalid credentials, 404 for not found, and 422 for validation errors — Pydantic automatically returns 422 with detailed error messages."
