# Dependency Analysis

## Backend runtime

| Dependency/group | Why it exists | Imported by | Removal/alternative |
|---|---|---|---|
| FastAPI, Uvicorn | HTTP API and server | `main.py` | Required unless replacing web stack |
| SQLAlchemy | ORM/session lifecycle | `database.py`, `main.py` | Replace with SQLModel or raw SQLite, not recommended casually |
| python-jose | JWT encoding/decoding | `auth.py` | PyJWT is an alternative |
| Passlib/Bcrypt | password hashing | `auth.py` | Argon2id is a stronger modern alternative; current Bcrypt version compatibility must be fixed |
| python-dotenv | `.env` loading | backend modules | Replace with deployment environment injection |
| PyTorch/Transformers | DistilBERT inference/training | model/training modules | Required for current model |
| SentenceTransformers | semantic embeddings | `rag/embeddings.py` | Hosted embeddings or Transformers pooling |
| FAISS CPU | vector search abstraction | `rag/faiss_store.py` | Qdrant, pgvector, Elasticsearch, or remove if advanced path is retired |
| Requests/HTTPX | provider HTTP calls | retrieval/LLM modules | Standard library is insufficiently ergonomic |
| BeautifulSoup/lxml | content extraction | retriever | Readability/Trafilatura alternatives |
| LangGraph | graph-compatible orchestration | agents | Plain service calls could simplify the active deterministic path |
| Groq/OpenAI/Google SDKs | provider integrations | `llm_client.py` | Keep only providers actually supported |
| NewsAPI/SerpAPI/Tavily SDKs | evidence providers | retriever/clients | Keep based on provider strategy |
| Neo4j driver | optional graph store | `graph.py` | Remove if Neo4j remains disabled |
| ReportLab | PDF export | `pdf_export.py` | WeasyPrint or browser print |
| Feedparser/DDG search | auxiliary/legacy retrieval | backend retrieval | Review actual active imports before removal |

## Frontend

| Dependency | Use |
|---|---|
| React / React DOM | UI runtime |
| React Router DOM | page routing |
| Axios | API transport |
| Vite / React plugin | development/build |
| Framer Motion / AOS | restrained transitions/legacy animation support |
| Lucide React | icons |
| Chart.js / react-chartjs-2 | statistics charts |
| Popper / React Popper | positioned UI |
| clsx / tailwind-merge | class composition utilities |
| ESLint plugins | static analysis |

## Cleanup candidates

The project should verify imports before removing Feedparser, DuckDuckGo, OpenAI, DeepSeek configuration, AOS, Popper, or archived deployment assumptions. Removing a dependency is safe only after route/build/tests prove no active import remains.
