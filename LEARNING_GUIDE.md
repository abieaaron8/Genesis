# Learning Guide

## The pieces

- **React** renders the browser interface and manages local state.
- **FastAPI** exposes Python functions as HTTP endpoints.
- **Axios** sends JSON requests from the browser.
- **SQLite** stores users, history, and cache records in a file.
- **DistilBERT** is a smaller Transformer classifier trained on WELFake.
- **Search providers** return candidate articles and pages.
- **RAG** means retrieving relevant text and giving that context to a reasoning step.
- **LLMs** can summarize or reason over supplied context, but they must not be treated as evidence themselves.

## A request in plain language

The browser sends a claim to FastAPI. FastAPI asks the local classifier for a signal, searches for evidence, ranks and labels the evidence, asks prosecutor/defender roles to compare it, and asks the judge stage to synthesize a result. The response travels back as JSON and React renders it.

## Why retrieval matters

A classifier recognizes patterns from training data; it does not know every new event. Retrieval supplies current source material. Ranking helps the system prioritize relevant and credible documents. RAG is the pattern of combining that retrieved context with a reasoning prompt.

## Why there are multiple agents

The prosecutor and defender roles force the pipeline to consider both directions. The judge is a synthesis step. In Genesis, deterministic logic is the default, with optional LLM calls controlled by flags.

## Where to start coding

1. Read `frontend/react-app/src/pages/Home.jsx` to understand the user journey.
2. Read `frontend/react-app/src/services/api.js` for HTTP contracts.
3. Read `backend/main.py` around `verify_claim()`.
4. Follow `backend/agents.py` into `backend/rag/` and `backend/agents/`.
5. Read `backend/database.py` for persistence.
6. Run `/docs` and inspect `/openapi.json` while developing.

## Safe experimentation

Use deterministic mode and provider mocks first. Never test with production keys or real user data. Log stage names and timing, not secret values or unrestricted external content.
