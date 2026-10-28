# Environment Loading Audit

## Result

Backend provider configuration now loads deterministically from:

`backend/.env`

The provider modules no longer depend on the process working directory when
they are imported directly or through Uvicorn.

## Findings

- `python-dotenv` is installed and available.
- `backend/__init__.py` already loaded the backend-local `.env`.
- `backend/rag/retriever.py` already loaded the backend-local `.env`.
- `backend/llm_client.py` and `backend/rag/tavily_client.py` previously used
  plain `load_dotenv()`, which could resolve a different file depending on the
  launch directory and import context.
- `GEMINI_API_KEY`, `TAVILY_API_KEY`, and `NEWS_API_KEY` are present and
  non-empty in `backend/.env`.
- `NEWSAPI_KEY` is also present but contains a placeholder value and is ignored
  when the valid `NEWS_API_KEY` is available.
- `GOOGLE_API_KEY` is not present. Gemini uses the configured
  `GEMINI_API_KEY`, so no fallback variable is required.

## Changes

- Updated `backend/llm_client.py` to load `backend/.env` using an explicit
  path derived from the module location.
- Updated `backend/rag/tavily_client.py` to use the same explicit backend-local
  dotenv path.
- No API routes, application logic, UI code, or secrets were changed.

## Verification

- Safe runtime presence checks confirmed the configured provider variables
  without printing secret values.
- A fresh Uvicorn startup completed application initialization.
- Startup output changed to:

  `[LLM] Gemini: ready`

- The backend responded successfully with HTTP 200 on `/openapi.json`.
