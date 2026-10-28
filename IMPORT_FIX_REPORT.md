# Backend import fix report

## Result

The backend now imports and starts from the repository root with:

```powershell
python -m uvicorn backend.main:app --reload
```

Verification:

- `import backend.main` completed successfully.
- Uvicorn started from the project root.
- `GET http://127.0.0.1:8000/openapi.json` returned HTTP 200.
- Backend Python files compile successfully.
- No remaining bare local imports were found under `backend/`.

## Import changes

| File | Previous import | Replacement |
|---|---|---|
| `backend/main.py` | `agents`, `auth`, `credibility`, `services.*`, `database`, `filters`, `graph`, `pdf_export`, `rag_core` | `backend.agents`, `backend.auth`, `backend.credibility`, `backend.services.*`, `backend.database`, `backend.filters`, `backend.graph`, `backend.pdf_export`, `backend.rag_core` |
| `backend/main.py` | `rag.retriever` | `backend.rag.retriever` |
| `backend/main.py` | `llm_client` | `backend.llm_client` |
| `backend/agents.py` | `claim_analyzer`, `defender`, `judge`, `prosecutor` | `backend.agents.claim_analyzer`, `backend.agents.defender`, `backend.agents.judge`, `backend.agents.prosecutor` |
| `backend/agents.py` | `rag.retriever`, `services.credibility_service`, `state` | `backend.rag.retriever`, `backend.services.credibility_service`, `backend.state` |
| `backend/auth.py` | `database` | `backend.database` |
| `backend/credibility.py` | `services.credibility_service` | `backend.services.credibility_service` |
| `backend/rag_core.py` | `legacy_rag_core` | `backend.legacy_rag_core` |
| `backend/legacy_rag_core.py` | `credibility` | `backend.credibility` |
| `backend/services/ranking_service.py` | `credibility` | `backend.credibility` |
| `backend/services/evidence_classifier.py` | `llm_client` | `backend.llm_client` |
| `backend/agents/claim_analyzer.py` | `llm_client` | `backend.llm_client` |
| `backend/agents/judge.py` | `llm_client` | `backend.llm_client` |
| `backend/agents/prosecutor.py` | `llm_client`, `services.evidence_classifier` | `backend.llm_client`, `backend.services.evidence_classifier` |
| `backend/agents/defender.py` | `llm_client`, `services.evidence_classifier` | `backend.llm_client`, `backend.services.evidence_classifier` |
| `backend/rag/retriever.py` | `credibility`, `llm_client`, `rag.*`, `services.ranking_service` | `backend.credibility`, `backend.llm_client`, `backend.rag.*`, `backend.services.ranking_service` |
| `backend/rag/tavily_client.py` | `credibility` fallback import | `backend.credibility` |

## Legacy agent module compatibility

The repository contains both `backend/agents.py` and `backend/agents/`. Python selects
`backend.agents` as the module file, so `backend/agents.py` now exposes the existing
`backend/agents/` directory through `__path__` before importing its submodules. This
preserves the current graph entry point while allowing the agent modules to use
package-qualified imports from the project root.

No application logic, endpoint behavior, or model behavior was changed.
