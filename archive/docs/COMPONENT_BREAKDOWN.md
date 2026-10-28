# Component Breakdown

## Backend

| File | Purpose | Important symbols / responsibilities |
|---|---|---|
| `backend/main.py` | Composition root and API | `app`, `verify_claim`, auth/history/health/stats/export routes, middleware, startup |
| `backend/agents.py` | Pipeline graph | `decompose_claim`, `run_claim_graph`, analysis/retrieval/debate/judge nodes |
| `backend/state.py` | Shared state | Verification state carried between nodes |
| `backend/auth.py` | Security | password hash, JWT encode/decode, current-user dependencies |
| `backend/database.py` | Persistence | `User`, `ClaimHistory`, `ClaimCache`, sessions, cache helpers |
| `backend/llm_client.py` | Provider client | provider readiness, routing, JSON extraction, fallback |
| `backend/graph.py` | Optional graph store | Neo4j connection and reputation/entity operations; disabled by default |
| `backend/rag/retriever.py` | Retrieval | provider calls, normalization, filtering, scoring, minimal/advanced paths |
| `backend/rag/tavily_client.py` | Tavily adapter | request and result normalization |
| `backend/rag/embeddings.py` | Embeddings | SentenceTransformer singleton and fallback vectors |
| `backend/rag/faiss_store.py` | Vector abstraction | in-memory FAISS indexing/search |
| `backend/services/model_service.py` | ML inference | lazy singleton, device choice, prediction output |
| `backend/services/ranking_service.py` | Ranking | article relevance and confidence calculations |
| `backend/services/credibility_service.py` | Source scoring | domain, freshness, specificity, consistency |
| `backend/services/evidence_classifier.py` | Stance | supports/contradicts/neutral classification |
| `backend/services/cache_service.py` | Cache helpers | claim hashing/cache state |
| `backend/services/metrics_service.py` | Observability | latency and pipeline metrics |
| `backend/agents/claim_analyzer.py` | Analysis | domain/type classification, optional analyzer LLM |
| `backend/agents/prosecutor.py` | Debate role | argument against claim |
| `backend/agents/defender.py` | Debate role | argument supporting claim |
| `backend/agents/judge.py` | Decision role | known facts, synthesis, deterministic fallback |
| `backend/pdf_export.py` | Reporting | ReportLab PDF generation |
| `backend/filters.py` | Evidence filters | trusted-source prioritization and quality filtering |

## Training and inference

`backend/training/dataset.py`, `preprocess.py`, `train.py`, `evaluate.py`, and `predict.py` form the reproducible ML workflow. `backend/inference/predictor.py` is an older standalone predictor interface; the active API uses `services/model_service.py`.

## Frontend

| File/group | Responsibility |
|---|---|
| `src/main.jsx` | React root and BrowserRouter |
| `src/App.jsx` | Routes, session bootstrap, logout, theme |
| `src/pages/Home.jsx` | Main verification workspace and response rendering |
| `src/pages/History.jsx` | History list and navigation |
| `src/pages/Stats.jsx` | Chart.js statistics |
| `src/pages/Login.jsx`, `Register.jsx` | Auth forms |
| `src/pages/Profile.jsx` | Current-user profile/settings |
| `src/services/api.js` | Axios transport and auth headers |
| `src/components/*` | Evidence, confidence, verdict, agents, loading UI |
| `src/App.css`, `src/index.css` | Application and global styling |
| `src/lib/utils.ts` | Shared frontend utilities |

## Active versus archived

Files under `archive/` are historical implementations/configurations and are not assumed by the active import graph.
