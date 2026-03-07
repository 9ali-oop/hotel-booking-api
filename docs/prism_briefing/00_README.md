# PRISM BRIEFING — Hotel Booking Intelligence API
# How to use this directory with OpenAI Prism

---

## What is in this directory?

| File | Purpose |
|------|---------|
| `01_PRISM_PROMPT.md` | **START HERE** — the master instructions for Prism |
| `02_PROJECT_CONTEXT.md` | Complete technical facts about the project |
| `03_KEY_CODE_SNIPPETS.md` | Representative code for LaTeX listings |
| `04_REFERENCES.md` | All academic/industry references (Harvard format) |

---

## How to use with Prism

1. Go to **https://openai.com/prism** — sign in with your ChatGPT account
2. Click **New Project**
3. In the project, open a new document
4. Copy-paste the contents of **`01_PRISM_PROMPT.md`** first
5. Then paste **`02_PROJECT_CONTEXT.md`**, **`03_KEY_CODE_SNIPPETS.md`**, and **`04_REFERENCES.md`** below it (all in one message or as separate uploads — try both)
6. Hit generate and let GPT-5.2 write the LaTeX document
7. Review, adjust any factual details, compile to PDF
8. Download the PDF and save it as `docs/technical_report_prism.pdf`

---

## Tips for getting the best output

- If Prism generates partial content, ask it to continue with: *"Please continue from Section [X]"*
- For each TikZ diagram, if it doesn't render correctly, ask: *"Regenerate the [architecture/pipeline/ER] diagram as a simpler TikZ figure"*
- You can upload a photo of a hand-drawn sketch and ask Prism to convert it to a proper TikZ diagram
- If any technical detail looks wrong, correct it in the chat: *"The JWT expiry is 30 minutes, not 60"*
- Ask Prism to compile after each major section to catch LaTeX errors early

---

## What the marker is looking for (Outstanding band, 90–100)

- Critical evaluation of technology choices (not just listing them)
- Justification for design decisions with reference to literature
- Evidence of understanding security implications (auth, timing attacks)
- Professional presentation (LaTeX typesetting far exceeds Word/DOCX)
- Diagrams that clearly communicate architecture
- Honest limitations and future work
- Proper Harvard references (minimum 8)
- Generative AI usage declared transparently
