# Genesis v1 Repository Cleanup Analysis

## Classification Criteria
- **KEEP**: Required for Genesis v1 core functionality (FastAPI + React + Tailwind + Multi-agent RAG + LLM fallbacks)
- **ARCHIVE**: Legacy, duplicate, experimental, or future-version code that should be preserved but not active
- **DELETE**: Completely unnecessary (test artifacts, PID files, redundant configs)

---

## BACKEND CLASSIFICATION

### Root Backend Files

| File | Classification | Reason |
|------|---------------|--------|
| `main.py` | **KEEP** | Core FastAPI application with all endpoints, pipeline orchestration, and verdict logic |
| `requirements.txt` | **KEEP** | Python dependencies for Genesis v1 |
| `agents.py` | **KEEP** | LangGraph orchestrator for multi-agent pipeline |
| `state.py` | **KEEP** | Pydantic VerificationState for LangGraph |
| `rag_core.py` | **KEEP** | Re-exports legacy functions still used (build_context, rank_with_faiss) |
| `llm_client.py` | **KEEP** | Multi-LLM fallback chain (Gemini → Groq → Ollama) - core to Genesis v1 |
| `gemini_client.py` | **ARCHIVE** | Legacy Gemini-only client, superseded by llm_client.py |
| `database.py` | **KEEP** | SQLAlchemy models, cache, history persistence |
| `auth.py` | **KEEP** | JWT authentication (required for user features) |
| `credibility.py` | **KEEP** | Wrapper for credibility_service (0-1 score API) |
| `filters.py` | **KEEP** | Source quality filters (trusted/low-quality domains) |
| `pdf_export.py` | **KEEP** | PDF report generation (Genesis v1 requirement) |
| `graph.py` | **ARCHIVE** | Neo4j knowledge graph - optional, disabled in v1 (ENABLE_NEO4J=False) |
| `credibility.py` | **KEEP** | Compatibility wrapper |
| `start.sh` | **ARCHIVE** | Startup script, not needed with uvicorn directly |
| `wait_for_ollama.py` | **ARCHIVE** | Utility script, not core |
| `validate_api_keys.py` / `verify_keys.py` | **ARCHIVE** | Validation scripts, not runtime code |
| `validate_hardening.py` / `validate_full_suite.py` / `validate_extended.py` | **ARCHIVE** | Test validation scripts |
| `diagnose.py` | **ARCHIVE** | Diagnostic script |
| `test_*.py` (all test files in backend/) | **ARCHIVE** | Test files moved to archive/tests/ |
| `uvicorn.pid` / `run_backend.pid` | **DELETE** | PID files - runtime artifacts |

### Backend Agents

| File | Classification | Reason |
|------|---------------|--------|
| `agents/claim_analyzer.py` | **KEEP** | Claim analysis, domain classification, entity extraction |
| `agents/prosecutor.py` | **KEEP** | Prosecutor agent (challenges claims) |
| `agents/defender.py` | **KEEP** | Defender agent (supports claims) |
| `agents/judge.py` | **KEEP** | Judge agent (synthesizes verdict) |
| `agents/source_tracker.py` | **ARCHIVE** | Unused legacy module |
| `agents/__init__.py` | **KEEP** | Package init |

### Backend RAG

| File | Classification | Reason |
|------|---------------|--------|
| `rag/retriever.py` | **KEEP** | Core evidence retrieval with multi-API fallback |
| `rag/embeddings.py` | **KEEP** | SentenceTransformer embeddings with fallback |
| `rag/faiss_store.py` | **KEEP** | FAISS vector store for semantic ranking |
| `rag/tavily_client.py` | **KEEP** | Tavily search API client |
| `rag/knowledge_base.py` | **ARCHIVE** | Legacy knowledge base, not used in v1 |
| `rag/realtime_fetcher.py` | **ARCHIVE** | Unused real-time fetcher |
| `rag/__init__.py` | **KEEP** | Package init |

### Backend Services

| File | Classification | Reason |
|------|---------------|--------|
| `services/ranking_service.py` | **KEEP** | Evidence ranking, keyword extraction, confidence calculation |
| `services/credibility_service.py` | **KEEP** | Dynamic credibility scoring (domain + freshness + specificity) |
| `services/evidence_classifier.py` | **KEEP** | Evidence stance classification (SUPPORTS/CONTRADICTS/NEUTRAL) |
| `services/cache_service.py` | **KEEP** | Semantic cache utilities |
| `services/metrics_service.py` | **KEEP** | Pipeline metrics logging |
| `services/llm_client.py` | **ARCHIVE** | Duplicate of root llm_client.py |
| `services/__init__.py` | **KEEP** | Package init |

### Backend Legacy (Entire Folder)

| Path | Classification | Reason |
|------|---------------|--------|
| `legacy/` | **ARCHIVE** | Entire legacy folder - superseded by current implementations |

### Backend Tests

| Path | Classification | Reason |
|------|---------------|--------|
| `tests/` | **ARCHIVE** | All test files - keep for reference but not in active codebase |

### Backend Data

| File | Classification | Reason |
|------|---------------|--------|
| `data/news_articles.json` | **KEEP** | Fallback dataset for retrieval |
| `data/faiss_vectors.npy` / `faiss_index.bin` | **ARCHIVE** | Pre-computed embeddings, can be regenerated |

---

## FRONTEND CLASSIFICATION

### Root Frontend Files

| File | Classification | Reason |
|------|---------------|--------|
| `package.json` | **KEEP** | Dependencies for React 19 + Vite + Tailwind |
| `package-lock.json` | **KEEP** | Lock file for reproducible installs |
| `vite.config.js` | **KEEP** | Vite configuration |
| `eslint.config.js` | **KEEP** | Linting config |
| `index.html` | **KEEP** | HTML entry point |
| `nginx.conf` | **ARCHIVE** | Docker nginx config, not needed for local dev |
| `Dockerfile` | **ARCHIVE** | Docker build file |
| `start.sh` | **ARCHIVE** | Startup script |
| `README.md` | **ARCHIVE** | Frontend-specific readme |

### Frontend Source

| File | Classification | Reason |
|------|---------------|--------|
| `src/main.jsx` | **KEEP** | App entry point |
| `src/App.jsx` | **KEEP** | Root component with routing, auth, theme |
| `src/App.css` | **KEEP** | Global styles (Tailwind via CSS variables) |
| `src/index.css` | **KEEP** | CSS variables, themes, base styles |
| `src/lib/utils.ts` | **KEEP** | Utility functions |

### Frontend Pages

| File | Classification | Reason |
|------|---------------|--------|
| `src/pages/Home.jsx` | **KEEP** | Main verification UI (core feature) |
| `src/pages/History.jsx` | **KEEP** | Claim history with replay |
| `src/pages/Stats.jsx` | **KEEP** | Analytics dashboard |
| `src/pages/Login.jsx` | **KEEP** | Authentication |
| `src/pages/Register.jsx` | **KEEP** | User registration |
| `src/pages/Profile.jsx` | **KEEP** | User profile/settings |

### Frontend Components

| File | Classification | Reason |
|------|---------------|--------|
| `src/components/AgentCard.jsx` | **KEEP** | Prosecutor/Defender argument display |
| `src/components/EvidenceCard.jsx` | **KEEP** | Evidence source display with credibility |
| `src/components/ConfidenceGauge.jsx` | **KEEP** | Confidence visualization |
| `src/components/VerdictBadge.jsx` | **KEEP** | Verdict badge component |
| `src/components/PipelineProgress.jsx` | **KEEP** | Real-time pipeline stage display |
| `src/components/SkeletonCard.jsx` | **KEEP** | Loading skeleton |
| `src/components/SkeletonLoader.jsx` | **ARCHIVE** | Duplicate/legacy skeleton |
| `src/components/MetricsPanel.jsx` | **ARCHIVE** | Unused metrics panel |
| `src/components/ConfidenceMeter.jsx` | **ARCHIVE** | Duplicate of ConfidenceGauge |

### Frontend Hooks & Services

| File | Classification | Reason |
|------|---------------|--------|
| `src/hooks/useVoice.js` | **ARCHIVE** | Voice input/output - optional, not core v1 |
| `src/services/api.js` | **KEEP** | Axios API client with auth |

### Frontend Assets

| File | Classification | Reason |
|------|---------------|--------|
| `src/assets/react.svg` | **DELETE** | Default Vite asset, unused |
| `src/assets/vite.svg` | **DELETE** | Default Vite asset, unused |
| `src/assets/hero.png` | **ARCHIVE** | Hero image, can be replaced |
| `public/icons.svg` | **KEEP** | Icon sprite |
| `public/favicon.svg` | **KEEP** | Favicon |

### Frontend Tests

| File | Classification | Reason |
|------|---------------|--------|
| `src/__tests__/Home.test.jsx` | **ARCHIVE** | Test file |

---

## ROOT LEVEL FILES

| File | Classification | Reason |
|------|---------------|--------|
| `README.md` | **ARCHIVE** | VeritasAI readme, will be replaced with Genesis readme |
| `README_FINAL_BACKUP.md` | **DELETE** | Backup file |
| `PROJECT_RUNTIME_CONTEXT.md` | **ARCHIVE** | Context doc for previous project |
| `HOW_TO_RUN.md` | **ARCHIVE** | Run guide for VeritasAI |
| `docker-compose.yml` | **ARCHIVE** | Docker config with Neo4j (optional profile) |
| `.env.example` (if exists) | **ARCHIVE** | Example env file |

---

## SUMMARY STATISTICS

| Category | Count |
|----------|-------|
| **KEEP** | ~45 files |
| **ARCHIVE** | ~55 files |
| **DELETE** | ~5 files |

---

## GENESIS v1 ARCHITECTURE ALIGNMENT

### ✅ Already Aligned (KEEP)
- FastAPI + React + Vite stack
- Multi-agent pipeline (Prosecutor/Defender/Judge) via LangGraph
- FAISS semantic ranking + hybrid retrieval
- Multi-LLM fallback (Gemini → Groq → Ollama)
- JWT authentication + user history
- PDF export
- Evidence credibility scoring
- Responsive UI with Framer Motion animations

### 🔄 To Be Added Later (Not in Current Codebase)
- Custom DistilBERT classifier (replaces keyword-based evidence_classifier)
- Live web search (Tavily already integrated, needs activation)
- Semantic evidence ranking (already present via FAISS)
- Explainable verdict (already present via reasoning_points)

### ❌ Removed from Active Codebase (ARCHIVE)
- Neo4j knowledge graph (optional, disabled)
- Legacy RAG implementations
- DeepSeek/Groq as primary (now fallback only)
- Voice input/output hooks
- Test files
- Diagnostic/validation scripts

---

## NEXT STEPS

1. Move all ARCHIVE files to `archive/` folder preserving structure
2. Delete identified DELETE files
3. Verify project still builds and runs
4. Update README.md for Genesis v1
5. Create Genesis v1 specific documentation