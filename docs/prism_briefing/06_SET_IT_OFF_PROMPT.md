# "SET IT OFF" PROMPT FOR PRISM
# Copy everything below the line and paste it as your first message in Prism.

---

You have access to 4 context files in this directory. Read ALL of them before generating anything:

- `01_PRISM_PROMPT.md` — master instructions (section order, formatting, diagram specs)
- `02_PROJECT_CONTEXT.md` — every technical fact about the project
- `03_KEY_CODE_SNIPPETS.md` — 7 code listings to embed as LaTeX lstlistings
- `04_REFERENCES.md` — 14 Harvard-format references to cite throughout

**Your job:** Generate a complete, compilable LaTeX document (`report` class, A4, 11pt) for the Hotel Booking Intelligence API technical report.

**HARD CONSTRAINT: 5-page maximum for body content.** Title page, abstract, ToC, references, and appendices do NOT count. This means every sentence in the body must earn its place. The strategy is: dense argumentative prose in the body, space-hungry elements (large tables, some diagrams, code listings) pushed to appendices.

**Critical quality bar:** This is for the 90–100 (Outstanding) band. That means:
1. **Every section needs 1–2 paragraphs of dense, argumentative prose** — not bullet points, not 1-sentence summaries. The marker wants to see *why* decisions were made, what alternatives were considered, and what trade-offs exist.
2. **Weave in-text citations into every section.** All 14 references must be cited at least once. Use Harvard format: (Author, Year).
3. **Keep ONLY 3 TikZ diagrams in the body** (architecture, AI pipeline, ER diagram) — scaled to ~60% width. Move the request flow and CI/CD pipeline diagrams to an appendix.
4. **Move ALL code listings to an appendix.** Reference them from the body with "see Appendix C, Listing X".
5. **Move the full 20+ endpoint table to an appendix.** In the body, summarise it in 1 sentence: "The API exposes 21 RESTful endpoints across five resource groups (see Appendix A)."
6. **Include these mandatory links in Section 1 (Introduction) as clickable `\href{}` links:**
   - GitHub repository: https://github.com/9ali-oop/hotel-booking-api
   - Live API base URL: https://web-production-c9799.up.railway.app/
   - Interactive API docs (Swagger UI): https://web-production-c9799.up.railway.app/docs
   - Live intelligence dashboard: https://web-production-c9799.up.railway.app/dashboard
   - Presentation slides: [leave as placeholder URL — to be added before submission]
7. **GenAI declaration:** 2 dense paragraphs covering tools used, what was AI-generated vs human-written, and ethical reflection on AI-assisted development.
8. **Four appendices (unlimited pages):**
   - Appendix A: Full Endpoint Table (all 20+ endpoints)
   - Appendix B: Additional Diagrams (request flow, CI/CD pipeline TikZ diagrams)
   - Appendix C: Key Code Listings (all 7 from the snippets file)
   - Appendix D: GenAI Conversation Logs (placeholder representative excerpts)
9. **Use `\appendix` command** so appendices render as "Appendix A", "Appendix B" etc., not numbered sections.

The body must be LASER-FOCUSED: 5 pages of dense, citation-rich prose that argues for every design decision. All supporting evidence (tables, diagrams, code) lives in the appendices where it has unlimited space.

Start generating the full document now. Do not stop partway — produce the complete LaTeX from `\documentclass` to `\end{document}`.
