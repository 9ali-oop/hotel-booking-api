# PRISM FEEDBACK — Rubric Cross-Reference & Improvement Instructions

## Paste this into Prism after your first draft to get it to fix everything.

---

## FEEDBACK PROMPT — PASTE THIS INTO PRISM:

---

I've had the report reviewed against the exact COMP3011 marking rubric. The current draft is a solid skeleton but it reads like an outline — every section is 1–3 sentences when it needs 1–2 paragraphs of critical, argumentative prose. The marker for the 90–100 (Outstanding) band expects "publication-quality documentation", "genuine research curiosity", and "creative application of Generative AI". Right now this is sitting at about 65–70 quality. Here is exactly what needs fixing, section by section.

### GLOBAL ISSUES

1. **The prose-to-diagram ratio is wrong.** The body is capped at 5 pages (appendices and references excluded). You're using those 5 pages, but too much space goes to TikZ diagrams and tables — the actual written prose is closer to 2 pages. You need to SHRINK the diagrams (make them smaller or move some to appendices) and PACK more argumentative prose into the freed space. Every paragraph must justify a design decision or cite a source. No wasted sentences.

2. **Almost zero in-text citations.** The reference list has 14 entries but only Antonio et al. (2019) is cited in the body. Every technology choice, every design pattern claim, every security argument MUST cite a source. For example: "FastAPI provides automatic OpenAPI documentation (FastAPI, 2024)", "JWT tokens follow RFC 7519 (Jones, Bradley and Sakimura, 2015)", "The OWASP API Security Top 10 identifies broken authentication as the leading API vulnerability (OWASP Foundation, 2023)". Weave citations into EVERY section.

3. **Missing mandatory submission links.** The rubric (page 18) explicitly requires the PDF to contain:
   - Link to the public GitHub repository (currently only on title page — add it in Section 1 as a clickable URL): https://github.com/9ali-oop/hotel-booking-api
   - Live deployed API base URL: https://web-production-c9799.up.railway.app/
   - Link to API documentation — the live Swagger UI is at: https://web-production-c9799.up.railway.app/docs
   - Link to the live interactive dashboard: https://web-production-c9799.up.railway.app/dashboard
   - Link to presentation slides (hosted on Google Drive or similar — add placeholder if not yet uploaded)
   - These MUST appear in the body text of Section 1 as clickable \href{} links, not just on the title page.

4. **Missing: GenAI conversation logs appendix.** The rubric says "GenAI declaration, analysis, and conversation logs as an appendix." The current Appendix A is code listings. You need an additional Appendix B with a structured GenAI usage log showing: which tools were used (Claude, ChatGPT/Prism, OpenAI API), for what purpose, what was generated vs. what was human-written, and a reflective analysis of how AI influenced the design process.

5. **Appendix A numbering bug.** It currently shows "1 Appendix A: Key Code Listings" — the section number should be removed or it should use \appendix command properly so it renders as "Appendix A" not "Section 1".

### SECTION-BY-SECTION FIXES

**Section 1 — Introduction (currently 2 short paragraphs → tighten to 1 dense paragraph + 1 scope paragraph)**
- Combine the economic context, dataset description (119,390 records, two Portuguese hotels, 32 features, 2015–2017), and project scope into two tight paragraphs. Cite Antonio et al. (2019). Don't waste space on a "report structure" paragraph — the ToC handles that. Every line must earn its place in the 5-page budget.

**Section 2 — Technology Stack & Justification (currently 1 paragraph → needs 2 dense paragraphs)**
This is the WORST section. The rubric wants "justification of design choices". Within the 5-page limit, compress this into 2 punchy paragraphs:
- Paragraph 1: Core stack — FastAPI over Flask (auto-docs, Pydantic validation, async-native), SQLAlchemy 2.0 over raw SQL (DB-agnostic ORM, migration-ready), SQLite over PostgreSQL (zero-config, read-heavy suitability, trade-off: limited write concurrency). Cite FastAPI (2024), SQLAlchemy (2024), Wiggins (2011).
- Paragraph 2: Supporting libraries — PyJWT for RFC 7519 compliance (cite Jones et al., 2015), slowapi for rate limiting (cite OWASP, 2023), httpx.AsyncClient for non-blocking LLM calls, pytest for test isolation (cite Krekel et al., 2024).
- DO NOT use subheadings — you can't afford the vertical space. Weave it into prose.

**Section 3 — System Architecture (currently 1 sentence + diagram → needs 1 paragraph + SMALLER diagram)**
- SHRINK the TikZ architecture diagram (it's eating too much page space). Make it ~60% of current size.
- Add 1 paragraph explaining: layered pattern benefits (separation of concerns, independent testability), FastAPI's Depends() for DI (per-request DB session enabling test isolation), Open/Closed Principle (new routers without modifying existing ones). Cite Fielding and Reschke (2014).

**Section 4 — API Design (currently abridged table + 1 sentence → full table in appendix, 1–2 paragraphs here)**
- MOVE the full 20+ endpoint table to Appendix A (it's too big for 5 pages). In the body, keep a SUMMARY sentence like "The API exposes 21 RESTful endpoints across five resource groups (see Appendix A)" and focus the prose on:
- 1 paragraph: REST principles — resource-oriented URIs, HTTP verb semantics, statelessness, pagination (skip/limit), filtering (hotel, country, is_canceled), status code semantics (200/201/400/401/403/404/422). Cite Fielding and Reschke (2014).
- 1 paragraph: Highlight the most interesting endpoints — analytics aggregations and the AI risk assessment — to show "novel data integration" per the Outstanding band.

**Section 5 — Authentication & Security (currently 1 paragraph + table → needs 2 dense paragraphs, keep table compact)**
- Paragraph 1: Dual auth rationale — API keys for M2M access, JWTs for session-based with 30-min expiry. Constant-time comparison via `hmac.compare_digest()` to prevent timing side-channels. Cite OWASP Foundation (2023), Jones et al. (2015).
- Paragraph 2: Rate limiting (60 req/min via slowapi), OWASP Top 10 alignment (API1, API2, API4), and honest limitations: no OAuth2 scopes, no RBAC, HTTPS delegated to Railway's reverse proxy. Cite Laurence (2023).
- Keep the auth table but make it COMPACT (reduce column widths).

**Section 6 — AI Integration (currently 1 paragraph + diagram → needs 2 paragraphs, SHRINK diagram)**
- SHRINK the AI pipeline TikZ diagram (~60% size). Move risk scoring weight table to appendix if space is tight.
- Paragraph 1: Heuristic scoring — weighted factors, 0.0–1.0 range, band thresholds. Prompt engineering — system persona, structured booking data, temperature 0.3, max_tokens 400. Cite OpenAI (2024).
- Paragraph 2: Graceful degradation — `_template_fallback()` returns schema-identical response when no API key is configured, ensuring the API contract never breaks. Ethical angle — heuristic is transparent/auditable vs black-box ML, LLM enriches but doesn't classify, human oversight preserved. Model-agnostic design via env var.

**Section 7 — Database Design (currently 2 sentences + diagram → 1 paragraph, SHRINK ER diagram)**
- SHRINK ER diagram to ~50% current size. 1 dense paragraph covering: three-table schema (bookings 32 cols, incidents FK, manager_notes FK), denormalisation justified (preserves dataset structure, normalising hotel types adds query complexity for no storage gain at 119K records), SQLite suitability (WAL mode, single-writer trade-off). Cite SQLAlchemy (2024).

**Section 8 — Testing Strategy (currently 1 sentence + table → 1 paragraph + compact table)**
- Keep the test count table but make it TIGHT. 1 paragraph: test pyramid (58 unit/integration, no E2E — acknowledged as limitation), in-memory SQLite per session for isolation and speed (0.87s), what's covered (auth gates, CRUD, filters, analytics, AI schema, edge cases), CI matrix (Python 3.10/3.11/3.12). Cite Krekel et al. (2024).

**Section 9 — Deployment & DevOps (currently 2 LINES → needs 1–2 paragraphs — CRITICALLY thin)**
- Paragraph 1: GitHub Actions CI — trigger on push/PR, three-version matrix, pytest. Railway deployment — git-based CD, Nixpacks detection, automatic HTTPS, env var injection. The project ships a live intelligence dashboard at https://web-production-c9799.up.railway.app/dashboard — served directly by FastAPI via `FileResponse` on `GET /dashboard`, demonstrating full-stack delivery beyond a raw API. Cite GitHub (2024).
- Paragraph 2: Twelve-factor alignment — one codebase, requirements.txt deps, env var config (API_KEY, JWT_SECRET, OPENAI_API_KEY, etc.), backing services as attached resources. Cite Wiggins (2011). This section MUST grow — it's worth marks under "Version Control & Deployment" (6 marks).

**Section 10 — Challenges & Solutions (currently 3 brief items → keep 3, make each 2–3 sentences)**
- Don't add more items (page budget). Instead make each existing challenge richer: what options were considered, why the chosen solution was best. Keep it tight.

**Section 11 — Evaluation & Limitations (currently 2 short paragraphs → 2 dense paragraphs)**
- Paragraph 1: Strengths + limitations in one sweep — layered architecture, dual auth, AI integration, 58 tests, BUT SQLite concurrency, no OAuth2/RBAC, heuristic not ML-trained, sync LLM calls.
- Paragraph 2: Future work + reflection — PostgreSQL migration, OAuth2 scopes, async task queue for LLM, trained ML model, what was learned about API design and testing discipline.

**Section 12 — GenAI Usage Declaration (currently bullet list → 2 dense paragraphs)**
- Paragraph 1: Tools used and how — Claude for code scaffolding/debugging/architecture, Prism for report drafting, OpenAI GPT-3.5-turbo as an integrated API feature. What was AI-generated vs human-written.
- Paragraph 2: Ethical reflection — how AI accelerated development, risks (over-reliance, uncritical acceptance), how human oversight was maintained (code review, manual refinement of generated output). The Outstanding band wants "creative application of Generative AI" — show it was thoughtful, not just copy-paste.

### CRITICAL: SPACE MANAGEMENT STRATEGY (5-PAGE LIMIT)

**Move these to appendices to free body space for prose:**
- The full 20+ endpoint table → Appendix A (reference from body with "see Appendix A")
- At least 2 of the 5 TikZ diagrams → Appendix B (keep the 3 most important in-body: architecture, AI pipeline, ER diagram. Move request flow and CI/CD pipeline to appendix.)
- All code listings → Appendix C
- GenAI conversation logs → Appendix D

**Keep in body but SHRINK:**
- Remaining 3 TikZ diagrams should be scaled to ~60% of current size using `\scalebox{0.6}{}` or `\resizebox{0.6\textwidth}{!}{}`
- Tables should use `\small` or `\footnotesize` font and tight column spacing

**The freed space goes to:** argumentative prose with in-text citations in every section. This is what separates a 70 from a 95.

### FORMATTING FIXES

- Fix Appendix numbering: use `\appendix` before appendix sections so they render as "Appendix A", "Appendix B" etc.
- Add `\usepackage{hyperref}` and make all URLs clickable with `\url{}` or `\href{}`
- Ensure every figure and table is referenced in the body text with `\ref{}`

### SUMMARY: WHAT THE MARKER WANTS FOR 90–100

The Outstanding band requires: exceptional originality (AI risk assessment + graceful degradation), novel data integration (119K records + analytics + LLM enrichment), publication-quality documentation (currently NOT met — needs dense prose with citations), genuine research curiosity (WHY not just WHAT), and creative GenAI application (structured reflection, not a bullet list).

The structure is correct. The diagrams are good. The references are sufficient. What's missing is DENSITY — within 5 pages, every sentence must justify a decision, cite a source, or discuss a trade-off. Move space-hungry elements (tables, diagrams, code) to appendices and fill the body with the argumentative prose that earns Outstanding marks.
