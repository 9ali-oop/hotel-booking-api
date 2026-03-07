# KEY CODE SNIPPETS FOR LISTINGS
# Include these in the LaTeX report as representative code examples

---

## Listing 1 — FastAPI Route with Dependency Injection (bookings.py)

```python
@router.get("/bookings", response_model=List[BookingResponse])
def list_bookings(
    hotel: Optional[str] = Query(None, description="Filter by hotel type"),
    country: Optional[str] = Query(None, description="Filter by country code"),
    is_canceled: Optional[int] = Query(None, ge=0, le=1),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Max records to return"),
    db: Session = Depends(get_db),
):
    """Retrieve bookings with optional filters and pagination."""
    query = db.query(Booking)
    if hotel:
        query = query.filter(Booking.hotel == hotel)
    if country:
        query = query.filter(Booking.country == country)
    if is_canceled is not None:
        query = query.filter(Booking.is_canceled == is_canceled)
    return query.offset(skip).limit(limit).all()
```

---

## Listing 2 — Authentication Dependency (auth.py)

```python
async def require_api_key(
    api_key: Optional[str] = Security(api_key_header),
    bearer: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
) -> str:
    """Accept either X-API-Key header or JWT Bearer token."""
    if api_key is not None:
        if hmac.compare_digest(api_key, API_KEY):   # constant-time comparison
            return "api_key_user"
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key."
        )
    if bearer is not None:
        payload = verify_jwt_token(bearer.credentials)
        return payload.get("sub", "jwt_user")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required.",
        headers={"WWW-Authenticate": "Bearer"},
    )
```

---

## Listing 3 — JWT Token Creation (auth.py)

```python
def create_jwt_token(subject: str = "api_user") -> dict:
    now = datetime.utcnow()
    expiry = now + timedelta(minutes=JWT_EXPIRY_MINUTES)   # 30 minutes
    payload = {
        "sub": subject,
        "iss": "hotel-booking-api",
        "iat": int(now.timestamp()),
        "exp": int(expiry.timestamp()),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": JWT_EXPIRY_MINUTES * 60,
        "issued_at": now.isoformat(),
        "expires_at": expiry.isoformat(),
    }
```

---

## Listing 4 — LLM Analysis Service (llm_analysis.py)

```python
async def generate_risk_assessment(
    booking: dict, risk_score: float, risk_band: str, risk_factors: list
) -> dict:
    """Call OpenAI GPT for a natural language risk assessment."""
    if not OPENAI_API_KEY:
        return _template_fallback(booking, risk_score, risk_band, risk_factors)

    prompt = f"""
Booking ID {booking['id']} at {booking['hotel']}:
- Lead time: {booking['lead_time']} days
- Market segment: {booking['market_segment']}
- Deposit type: {booking['deposit_type']}
- Previous cancellations: {booking['previous_cancellations']}
- Risk score: {risk_score:.2f} ({risk_band})
- Contributing factors: {', '.join(risk_factors)}

Provide a structured assessment with: Risk Summary, Key Risk Factors,
Recommended Actions, and Revenue Impact.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={
                "model": OPENAI_MODEL,          # gpt-3.5-turbo by default
                "temperature": 0.3,
                "max_tokens": 400,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            },
            timeout=30.0,
        )
    ...
```

---

## Listing 5 — Risk Scoring Heuristic (risk_scoring.py)

```python
def calculate_risk_score(booking) -> tuple[float, str, list[str]]:
    score = 0.0
    factors = []

    if booking.lead_time > 200:
        score += 0.25
        factors.append(f"Very long lead time ({booking.lead_time} days)")
    elif booking.lead_time > 100:
        score += 0.15
        factors.append(f"Long lead time ({booking.lead_time} days)")

    if booking.previous_cancellations >= 2:
        score += 0.30
        factors.append(f"Multiple prior cancellations ({booking.previous_cancellations})")
    elif booking.previous_cancellations == 1:
        score += 0.20
        factors.append("One prior cancellation")

    if booking.deposit_type == "No Deposit":
        score += 0.15
        factors.append("No deposit taken")

    if booking.market_segment == "Online TA":
        score += 0.10
        factors.append("Online travel agent booking")

    if booking.is_repeated_guest == 0:
        score += 0.10
        factors.append("First-time guest")

    if booking.booking_changes == 0:
        score += 0.10
        factors.append("No booking modifications made")

    score = min(score, 1.0)
    band = "HIGH" if score > 0.6 else ("MEDIUM" if score >= 0.3 else "LOW")
    return round(score, 2), band, factors
```

---

## Listing 6 — Test with Authentication (test_incidents.py)

```python
AUTH_HEADER = {"X-API-Key": "hotel-booking-dev-key-2025"}

class TestIncidentsCRUD:
    def test_create_incident(self, client, sample_booking):
        response = client.post("/incidents", json={
            "booking_id": sample_booking.id,
            "incident_type": "maintenance",
            "severity": "high",
            "description": "Air conditioning failure in room 101",
            "reported_by": "Front Desk",
        }, headers=AUTH_HEADER)
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "open"
        assert data["incident_type"] == "maintenance"

    def test_create_incident_no_auth(self, client, sample_booking):
        response = client.post("/incidents", json={
            "booking_id": sample_booking.id,
            "incident_type": "maintenance",
            "severity": "low",
            "description": "Test description here",
            "reported_by": "Test",
        })
        assert response.status_code == 401

    def test_create_incident_bad_key(self, client, sample_booking):
        response = client.post("/incidents", json={...},
            headers={"X-API-Key": "wrong-key"})
        assert response.status_code == 403
```

---

## Listing 7 — GitHub Actions CI Workflow (.github/workflows/ci.yml)

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
    - uses: actions/checkout@v4
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run tests
      run: pytest tests/ -v
```
