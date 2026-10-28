# Backend Architecture

## FastAPI application

`backend/main.py` is the active composition root. It creates `FastAPI(title="Genesis")`, configures logging and CORS, installs timing middleware, registers startup/shutdown hooks, defines request models, and exposes verification, authentication, history, analytics, health, sharing, and export routes.

## Request lifecycle

- Pydantic validates JSON input.
- Dependency injection supplies SQLAlchemy sessions and optional/current users.
- The route calls model, graph, retrieval, and agent services.
- Response shaping preserves frontend-compatible fields and legacy aliases.
- Authenticated verification results are persisted.

## Middleware and lifecycle

CORS allows local Vite origins, methods, headers, and credentials. Timing middleware adds `processing_time_seconds`. Startup initializes SQLite and optionally connects Neo4j; the active code disables Neo4j. Shutdown closes the graph client.

## Modules

| Module | Role |
|---|---|
| `main.py` | Composition root and HTTP API |
| `agents.py` | Graph-style orchestration and state transitions |
| `state.py` | Verification state model |
| `auth.py` | Bcrypt/Passlib password hashing and JWT |
| `database.py` | SQLAlchemy models and cache helpers |
| `rag/` | Search, normalization, embeddings, vector abstraction |
| `services/` | Reusable ranking, credibility, cache, metrics, and model services |
| `pdf_export.py` | ReportLab report generation |
| `filters.py` | Source and evidence filtering |
| `llm_client.py` | Groq/Gemini/Ollama provider routing |

## Dependency injection

`get_db()` yields a SQLAlchemy session and closes it in `finally`. `get_current_user()` validates bearer JWTs; optional-user dependencies permit guest verification and limited guest history.

## Known backend concerns

- Registration currently encounters the installed Passlib/Bcrypt 5 incompatibility in the audited environment.
- `/api/health` contains a `grok`/`groq` readiness-key mismatch.
- History detail/export ownership checks require review.
- The frontend calls `DELETE /api/claims/{id}`, but no active matching route was found.
