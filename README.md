# Hotel Booking Intelligence API

A data-driven RESTful API for hotel booking analysis and operational management, built for the COMP3011 Web Services and Web Data module at the University of Leeds.

## Overview

This API combines **119,390 historical hotel booking records** from the [Kaggle Hotel Booking Demand](https://www.kaggle.com/datasets/jessemostipak/hotel-booking-demand) dataset with user-generated operational data (incident reports and manager notes) to provide analytical insights and operational intelligence for hotel management.

### Key Features

- **Booking Data Exploration**: Browse and filter historical booking records with pagination
- **Incident Management (Full CRUD)**: Create, read, update, and delete operational incident reports linked to bookings
- **Manager Notes (CRUD)**: Attach internal notes to bookings for operational context
- **Analytics**: Cancellation rates, monthly demand patterns, market segment performance
- **Intelligent Insights**: Rule-based risk scoring to identify high-risk bookings, operational hotspot detection
- **Interactive Dashboard**: Frontend UI for visual analytics and CRUD operations
- **Auto-generated API Documentation**: Interactive Swagger UI at `/docs`
- **MCP Server**: Model Context Protocol integration — AI assistants can interact with this API as an MCP tool server
- **Production Middleware**: CORS, rate limiting (60 req/min), structured request logging, health-check endpoint
- **CI/CD**: GitHub Actions workflow runs the full test suite on every push

## Tech Stack

| Component      | Technology          | Justification                                                |
|----------------|---------------------|--------------------------------------------------------------|
| Language       | Python 3.10+        | Readable, well-suited for data-driven applications           |
| Framework      | FastAPI             | Auto-generates OpenAPI docs, built-in Pydantic validation    |
| ORM            | SQLAlchemy 2.0      | Industry-standard Python ORM, clean model definitions        |
| Database       | SQLite              | Zero-config, portable — runs immediately after cloning       |
| Testing        | pytest + httpx      | Fast, Pythonic test framework with HTTP client support        |
| Frontend       | HTML + JS + Chart.js| Single-file dashboard, no build step required                |
| Rate Limiting  | slowapi             | Token-bucket rate limiter for FastAPI (60 req/min default)   |
| MCP            | fastapi-mcp         | Exposes all endpoints as Model Context Protocol tools        |
| CI/CD          | GitHub Actions      | Automated testing on push across Python 3.10/3.11/3.12      |
| Deployment     | Railway             | Auto-deploy from GitHub with health-check monitoring         |

> **Note on SQLite**: SQLite was chosen for portability and zero-configuration deployment. The SQLAlchemy ORM abstraction means migrating to PostgreSQL requires only a connection string change.

## Quick Start

### Prerequisites
- Python 3.10 or higher
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/9ali-oop/hotel-booking-api.git
cd hotel-booking-api

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate      # Linux/Mac
# venv\Scripts\activate       # Windows

# Install dependencies
pip install -r requirements.txt
```

### Import the Dataset

```bash
python -m app.services.import_csv
```

This loads all 119,390 booking records from `data/hotel_bookings.csv` into the SQLite database. Takes approximately 15-30 seconds.

### Run the API

```bash
python run.py
```

The API will be available at:
- **API Root**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Dashboard**: http://localhost:8000/dashboard
- **Health Check**: http://localhost:8000/health
- **MCP Server**: http://localhost:8000/mcp

### Run Tests

```bash
python -m pytest tests/ -v
```

All 34 tests should pass. Tests use an in-memory SQLite database (no file I/O, no cleanup needed).

## Deployment

### Railway (Live Server)

This project includes `railway.toml` and `Procfile` for one-click deployment on [Railway](https://railway.com):

1. Push the repository to GitHub
2. Connect the GitHub repo in Railway's dashboard
3. Railway auto-detects the `Procfile` and deploys
4. The `/health` endpoint is used for deployment health monitoring

### MCP Server (Model Context Protocol)

The API doubles as an MCP server via the `fastapi-mcp` library. Any MCP-compatible AI assistant (Claude Desktop, etc.) can connect to it:

```json
{
  "mcpServers": {
    "hotel-booking-api": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

All API endpoints are automatically exposed as MCP tools, allowing AI assistants to query bookings, create incidents, run analytics, and perform risk analysis conversationally.

### CI/CD (GitHub Actions)

Every push to `main` triggers the CI workflow (`.github/workflows/ci.yml`), which:
- Runs all 34 tests across Python 3.10, 3.11, and 3.12
- Verifies the API starts successfully
- Verifies the health-check endpoint responds

## API Endpoints

### Bookings (Read-Only)
| Method | Endpoint          | Description                              |
|--------|-------------------|------------------------------------------|
| GET    | /bookings         | List bookings with filters & pagination  |
| GET    | /bookings/{id}    | Get a single booking                     |

### Incidents (Full CRUD)
| Method | Endpoint            | Description                  |
|--------|---------------------|------------------------------|
| POST   | /incidents          | Create incident              |
| GET    | /incidents          | List incidents with filters  |
| GET    | /incidents/{id}     | Get single incident          |
| PUT    | /incidents/{id}     | Full update                  |
| PATCH  | /incidents/{id}     | Partial update               |
| DELETE | /incidents/{id}     | Delete incident              |

### Manager Notes (CRUD)
| Method | Endpoint          | Description                  |
|--------|-------------------|------------------------------|
| POST   | /notes            | Create note                  |
| GET    | /notes            | List notes with filters      |
| GET    | /notes/{id}       | Get single note              |
| DELETE | /notes/{id}       | Delete note                  |

### Analytics
| Method | Endpoint                                | Description                          |
|--------|-----------------------------------------|--------------------------------------|
| GET    | /analytics/cancellation-rate            | Cancellation statistics              |
| GET    | /analytics/monthly-demand               | Booking counts by month              |
| GET    | /analytics/market-segment-performance   | Segment comparison with ADR          |

### Insights
| Method | Endpoint                          | Description                              |
|--------|-----------------------------------|------------------------------------------|
| GET    | /insights/high-risk-bookings      | Risk-scored bookings (configurable threshold) |
| GET    | /insights/operational-hotspots    | Incident concentration analysis          |

### Operations
| Method | Endpoint  | Description                              |
|--------|-----------|------------------------------------------|
| GET    | /health   | Health check with database connectivity  |
| GET    | /         | API root with endpoint navigation        |

## Production Features

### Rate Limiting
The API enforces a default rate limit of **60 requests per minute** per IP address using `slowapi`. Exceeding the limit returns HTTP 429 (Too Many Requests) with a `Retry-After` header.

### CORS
Cross-Origin Resource Sharing is enabled, allowing the frontend dashboard and external clients to call the API from any origin. In a production deployment, `allow_origins` would be restricted to specific domains.

### Structured Logging
All requests are logged with method, path, status code, and response time (ms) using Python's `logging` module. Example:
```
2026-03-06 15:26:59  INFO  hotel_api  GET /bookings -> 200 (12.3 ms)
```

### Health Check
The `/health` endpoint verifies database connectivity and returns the API version. Used by Railway and uptime monitors for deployment health monitoring.

## Project Structure

```
hotel-booking-api/
├── app/
│   ├── main.py              # FastAPI app, middleware, health check
│   ├── database.py          # SQLAlchemy engine and session config
│   ├── models.py            # ORM models (Booking, Incident, ManagerNote)
│   ├── schemas.py           # Pydantic validation schemas
│   ├── routers/
│   │   ├── bookings.py      # Booking data endpoints
│   │   ├── incidents.py     # Incident CRUD endpoints
│   │   ├── notes.py         # Manager notes CRUD endpoints
│   │   ├── analytics.py     # Aggregation and statistics endpoints
│   │   └── insights.py      # Intelligent analysis endpoints
│   └── services/
│       ├── import_csv.py    # Dataset import script
│       └── risk_scoring.py  # Cancellation risk heuristic
├── tests/                   # pytest test suite (34 tests, in-memory DB)
├── static/
│   └── index.html           # Frontend dashboard
├── data/
│   └── hotel_bookings.csv   # Kaggle dataset (119,390 records)
├── docs/                    # Technical report, API docs, conversation logs
├── .github/
│   └── workflows/ci.yml     # GitHub Actions CI pipeline
├── mcp_server.py            # MCP server integration
├── requirements.txt         # Python dependencies
├── Procfile                 # Railway deployment command
├── railway.toml             # Railway deployment config
├── runtime.txt              # Python version for deployment
└── run.py                   # Entry point
```

## Dataset

**Hotel Booking Demand** — 119,390 records across two hotels (Resort Hotel and City Hotel) from 2015-2017. Includes booking details such as lead time, arrival dates, guest counts, meal plans, market segments, distribution channels, room types, pricing (ADR), cancellation status, and special requests.

Source: https://www.kaggle.com/datasets/jessemostipak/hotel-booking-demand

## API Documentation

Interactive API documentation is automatically generated by FastAPI's OpenAPI integration:

- **Swagger UI** (interactive testing): http://localhost:8000/docs
- **ReDoc** (reference documentation): http://localhost:8000/redoc
- **OpenAPI JSON schema**: http://localhost:8000/openapi.json

All endpoints, parameters, request/response schemas, and error codes are fully documented and testable through Swagger UI. A static PDF reference is available at [`docs/api_documentation.pdf`](docs/api_documentation.pdf).

## Author

**Ali** — COMP3011 Web Services and Web Data, University of Leeds, 2025-2026

## Generative AI Declaration

This project used Generative AI tools as permitted under the module's Green Light AI policy. Full details are provided in the technical report. Tools used include ChatGPT 5.4 (Thinking) for design exploration and architectural evaluation, and Claude (Anthropic) for implementation, testing, and documentation. AI was used as a creative design exploration partner — not just for code generation, but for systematic evaluation of alternatives at every architectural decision point. Conversation logs are attached in `docs/genai_conversation_logs/`.
