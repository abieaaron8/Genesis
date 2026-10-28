# System Architecture

## High-level architecture

```mermaid
flowchart TB
  Browser[React + Vite browser app] --> Axios[Axios API client]
  Axios --> API[FastAPI application]
  API --> Auth[JWT and optional-user dependencies]
  API --> Model[ModelService: DistilBERT]
  API --> Graph[Verification orchestration]
  Graph --> Analyze[Claim analyzer]
  Graph --> Retrieve[Retriever]
  Retrieve --> Providers[Tavily / SerpAPI / NewsAPI / local fallback]
  Retrieve --> Rank[Relevance, credibility, freshness ranking]
  Graph --> Debate[Prosecutor and Defender]
  Debate --> Judge[Judge and verdict hardening]
  API --> DB[(SQLite via SQLAlchemy)]
  Judge --> API
  API --> Browser
```

## Layer architecture

| Layer | Active modules | Responsibility |
|---|---|---|
| Presentation | `frontend/react-app/src` | Routes, forms, result rendering, local UI state |
| Transport | `frontend/.../services/api.js`, FastAPI routes | HTTP requests and response contracts |
| Application | `backend/main.py`, `backend/agents.py` | Request lifecycle and pipeline orchestration |
| Domain | `backend/agents/`, `backend/services/` | Claim analysis, evidence stance, scoring, judgment |
| Infrastructure | `backend/rag/`, `backend/llm_client.py`, `backend/database.py` | Providers, model loading, storage |
| Training | `backend/training/` | WELFake preprocessing and DistilBERT fine-tuning |

## Component interaction

```mermaid
sequenceDiagram
  participant UI as React Home
  participant API as FastAPI /api/verify
  participant M as ModelService
  participant G as Verification graph
  participant R as Retriever
  participant L as Optional LLM
  participant DB as SQLite
  UI->>API: ClaimRequest
  API->>M: predict(claim)
  API->>G: run_claim_graph(state)
  G->>R: retrieve evidence
  R-->>G: normalized evidence
  G->>L: optional reasoning call
  G-->>API: agents, evidence, verdict
  API->>DB: save authenticated history
  API-->>UI: verification response
```

## Dependency graph

```mermaid
graph TD
  Main[backend/main.py] --> Agents[backend/agents.py]
  Main --> Database[backend/database.py]
  Main --> Model[backend/services/model_service.py]
  Agents --> Analyzer[agents/claim_analyzer.py]
  Agents --> Prosecutor[agents/prosecutor.py]
  Agents --> Defender[agents/defender.py]
  Agents --> Judge[agents/judge.py]
  Agents --> Retriever[rag/retriever.py]
  Retriever --> Tavily[rag/tavily_client.py]
  Retriever --> Embeddings[rag/embeddings.py]
  Main --> LLM[llm_client.py]
  Main --> Frontend[React client]
```

`archive/` is historical and is not part of the default runtime path.
