# Configuration Guide

Values belong in `backend/.env` or frontend `.env` files. Never commit secrets.

## Security and storage

| Variable | Default/behavior | Consumer |
|---|---|---|
| `SECRET_KEY` | Fallback exists in `auth.py`; set a strong production value | JWT auth |
| `CORS_ORIGINS` | Development localhost origins are configured | FastAPI CORS |
| `DATABASE_URL` | `sqlite:///./genesis.db` | SQLAlchemy/database |

## Retrieval

| Variable | Purpose |
|---|---|
| `TAVILY_API_KEY` | Tavily credentials |
| `TAVILY_SEARCH_DEPTH` | Tavily search depth |
| `TAVILY_MAX_RESULTS` | result count |
| `TAVILY_INCLUDE_RAW_CONTENT` | request raw content |
| `SERPAPI_KEY`, `SERPAPI_API_KEY` | SerpAPI credentials/compatibility |
| `NEWSAPI_KEY`, `NEWS_API_KEY` | NewsAPI credentials/compatibility |
| `GENESIS_USE_ADVANCED_RAG` | enable advanced retrieval/FAISS path; default `0` |
| `RAG_MAX_AGE_DAYS` | freshness window |
| `RAG_API_CACHE_TTL_SECONDS` | provider cache lifetime |
| `RAG_API_CACHE_MAX_ITEMS` | provider cache capacity |
| `GENESIS_DISABLE_ADVANCED_CACHE` | disables advanced cache by default |

## LLMs

`GROQ_API_KEY`, `GROQ_JUDGE_MODEL`, `GROQ_DEFENDER_MODEL`, `GEMINI_API_KEY`, `GEMINI_MODEL`, `DEEPSEEK_API_KEY`, `DEEPSEEK_BASE_URL`, `DEEPSEEK_MODEL`, `OLLAMA_BASE_URL`, `OLLAMA_ANALYZER_MODEL`, `OLLAMA_MODEL`, `GENESIS_DISABLE_OLLAMA`, `GROQ_RATE_LIMIT_COOLDOWN_SECONDS`, and `GEMINI_RATE_LIMIT_COOLDOWN_SECONDS` control provider credentials, models, URLs, cooldowns, and fallbacks. Active provider use is determined by `llm_client.py`; some DeepSeek/defender settings are compatibility or stale configuration.

## Feature switches

| Variable | Default | Effect |
|---|---:|---|
| `GENESIS_ENABLE_LLM_AGENTS` | `0` | optional prosecutor/defender/judge LLM reasoning |
| `GENESIS_ENABLE_CLAIM_ANALYZER_LLM` | `0` | optional analyzer LLM |
| `GENESIS_ENABLE_EVIDENCE_CLASSIFIER_LLM` | `0` | optional evidence stance LLM |
| `GENESIS_MODEL_PATH` | Genesis model artifact | override model location |
| `GENESIS_MAX_LENGTH` | model-service default | tokenizer sequence length |
| `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` | provider-specific | optional graph store; disabled by active main code |

## Frontend

`VITE_API_BASE_URL` controls Axios base URL. An empty value is suitable for same-origin deployment; local development normally points to `http://localhost:8000`.

## Security checklist

Use a random secret, rotate provider keys, restrict CORS in production, do not log prompts or secrets, protect history/PDF ownership, pin compatible bcrypt/passlib versions, and keep `.env` out of source control.
