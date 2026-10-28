# File Summary

The table lists every major active file/group discovered during the repository audit. Generated assets, dependency caches, datasets, and archived duplicates are intentionally grouped.

| File/group | Purpose | Used by | Importance |
|---|---|---|---|
| `backend/main.py` | FastAPI app and routes | Uvicorn, frontend | Critical |
| `backend/agents.py` | Verification orchestration | `main.py` | Critical |
| `backend/state.py` | Pipeline state | agents | High |
| `backend/auth.py` | JWT/password auth | routes | Critical |
| `backend/database.py` | ORM/storage | routes/startup | Critical |
| `backend/llm_client.py` | LLM providers | agents/main | High |
| `backend/rag/retriever.py` | Search and evidence | agents | Critical |
| `backend/rag/tavily_client.py` | Tavily adapter | retriever | High |
| `backend/rag/embeddings.py` | embeddings | advanced retrieval | Medium |
| `backend/rag/faiss_store.py` | vector search abstraction | advanced retrieval | Medium |
| `backend/services/model_service.py` | DistilBERT inference | main | Critical |
| `backend/services/ranking_service.py` | ranking | retrieval/main | High |
| `backend/services/credibility_service.py` | credibility | retrieval/main | High |
| `backend/services/evidence_classifier.py` | stance | agents | High |
| `backend/services/cache_service.py` | cache helpers | backend | Medium |
| `backend/services/metrics_service.py` | metrics/logging | pipeline | Medium |
| `backend/agents/claim_analyzer.py` | claim analysis | agents | High |
| `backend/agents/prosecutor.py` | contradicting argument | agents | High |
| `backend/agents/defender.py` | supporting argument | agents | High |
| `backend/agents/judge.py` | verdict synthesis | agents | Critical |
| `backend/pdf_export.py` | PDF reports | export routes | Medium |
| `backend/filters.py` | source filtering | retrieval | High |
| `backend/training/*` | ML training/evaluation | model artifact lifecycle | High |
| `backend/models/genesis_distilbert/*` | trained model/tokenizer/config | model service | Critical |
| `frontend/react-app/src/App.jsx` | frontend shell/routes | React root | Critical |
| `frontend/react-app/src/pages/*` | page-level features | App routes | Critical |
| `frontend/react-app/src/components/*` | reusable result UI | Home/pages | High |
| `frontend/react-app/src/services/api.js` | API client | pages | Critical |
| `frontend/react-app/src/*.css` | styling | React components | Medium |
| `frontend/react-app/index.html` | browser document shell | Vite | High |
| `backend/.env.example` | backend configuration template | operators | High |
| `frontend/react-app/.env.example` | frontend configuration template | operators | High |
| `backend/requirements.txt` | backend runtime dependencies | installation | Critical |
| `backend/training/requirements.txt` | training dependencies | ML workflow | High |
| `frontend/react-app/package.json` | frontend dependencies/scripts | npm | Critical |
| `archive/` | superseded code/configuration | none by default | Reference |
