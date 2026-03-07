# PRISM MASTER PROMPT
# Paste this entire file into Prism as your project brief

---

You are writing a professional technical report for university coursework. Please generate a complete, publication-quality LaTeX document based on the full project context provided below and in the accompanying files.

## Your Task

Produce a polished, academically rigorous technical report for a software engineering project titled **"Hotel Booking Intelligence API"**, submitted for COMP3011 Web Services and Web Data at the University of Leeds.

## Document Requirements

- **Format:** Full LaTeX document, `report` class, A4, 11pt, single-column
- **Length:** Maximum 5 pages of body content (excluding title page, abstract, ToC, references, and appendices). Appendices have unlimited pages — push tables, code listings, and secondary diagrams there. The body must be dense, citation-rich prose.
- **Language:** British English throughout
- **Style:** Academic but readable — explain technical decisions, not just what was built but *why*
- **Target band:** Outstanding (90–100) — the marker expects critical evaluation, justified design choices, and evidence of deep understanding

## Required Sections (in this order)

1. **Title Page** — project title, module code (COMP3011), university (University of Leeds), author (Ali), date (March 2026), GitHub URL (github.com/9ali-oop/hotel-booking-api)
2. **Abstract** — 150–200 words summarising the project, key contributions, and outcomes
3. **Table of Contents**
4. **1. Introduction** — project motivation, problem domain, hotel cancellation problem, dataset origin, scope
5. **2. Technology Stack & Justification** — every technology choice with academic/industry justification (not just a list — argue *why* each was chosen over alternatives)
6. **3. System Architecture** — layered architecture diagram (generate a TikZ diagram), request flow, dependency injection pattern
7. **4. API Design** — RESTful principles, endpoint catalogue table, resource modelling, HTTP semantics
8. **5. Authentication & Security** — dual auth system (API Key + JWT), security considerations (timing attacks, token expiry, statelessness), OWASP alignment
9. **6. AI Integration** — LLM-powered risk assessment, the pipeline diagram (generate a TikZ flow diagram), graceful degradation, prompt engineering choices, ethical considerations
10. **7. Database Design** — schema, ER diagram (generate TikZ), denormalisation decision, SQLite justification
11. **8. Testing Strategy** — 58 tests, test pyramid, coverage by module (table), in-memory SQLite approach, CI matrix
12. **9. Deployment & DevOps** — Railway deployment, GitHub Actions CI/CD pipeline diagram (TikZ), environment configuration
13. **10. Challenges & Solutions** — at least 3 real challenges with how they were resolved
14. **11. Evaluation & Limitations** — critical self-assessment, what could be improved (database scalability, OAuth2, async workers, etc.)
15. **12. Generative AI Usage Declaration** — honest, structured declaration of how AI tools were used in development and writing
16. **References** — minimum 8 academic/industry references, Harvard style

## Diagram Instructions

For each of the following, generate a **TikZ diagram** embedded in the LaTeX:

1. **Layered Architecture** (Section 3) — vertical stack: HTTP Layer → Auth Layer → Schema Layer → Service Layer → ORM Layer → Database. Use colored boxes, left-side accent bars, and downward arrows.

2. **Request Flow** (Section 4) — horizontal sequence: Client → FastAPI Router → Auth Check → Pydantic Schema → Service/ORM → SQLite → Response. Show the auth branch (401/403 for failed auth).

3. **AI Assessment Pipeline** (Section 6) — four steps: Fetch Booking → Risk Score → LLM Call (OpenAI GPT) → Return Assessment. Show the fallback branch (Template if no API key).

4. **ER Diagram** (Section 7) — three entities: bookings (many fields), incidents (FK to bookings), manager_notes (FK to bookings). Crow's-foot notation.

5. **CI/CD Pipeline** (Section 9) — GitHub push → Actions triggered → Install deps → pytest (3.10/3.11/3.12 matrix) → all pass → Railway deploy.

## Formatting Standards

- All code snippets in `lstlisting` with Python syntax highlighting
- All tables use `booktabs` package
- Headers and footers: module code left, page number right
- Proper `\label{}` and `\ref{}` for all figures, tables, listings
- Section headings with `\section{}`, subsections with `\subsection{}`
- No orphaned headings (use `\needspace` if needed)

## Full Project Context

All technical details are in the files accompanying this prompt:
- `02_PROJECT_CONTEXT.md` — complete technical facts
- `03_KEY_CODE_SNIPPETS.md` — representative code for listings
- `04_REFERENCES.md` — references to cite

Read all of them before generating the document.