# Verification Retrieval Trace

## Root cause

The repeated Gold/World War evidence came from the local fallback path, not
from Gemini or the frontend.

At the time of the failing request, the running Uvicorn process reported all
search providers as unavailable:

- Tavily: `TAVILY_API_KEY missing or disabled`
- NewsAPI: `NEWSAPI_KEY missing`
- SerpAPI: `SERPAPI_KEY missing`

Because `combined_articles` was empty, the minimal retriever loaded
`backend/data/news_articles.json`. Its fallback candidates included the two
observed articles. The stale running process had not loaded the corrected
backend-local dotenv configuration. A fresh process loaded the providers
correctly and stopped using the fallback dataset.

## Runtime flow

```text
POST /api/verify
  -> backend.main.verify_claim()
  -> backend.agents.decompose_claim()
  -> backend.agents.run_claim_graph()
  -> backend.agents._retriever_node()
  -> backend.rag.retriever.retrieve_evidence()
  -> retrieve_evidence_minimal() because VERITAS_USE_ADVANCED_RAG=0
  -> _gather_from_providers()
  -> search_tavily(), _search_serpapi(), _search_newsapi()
  -> filtering and ranking
  -> prosecutor / defender
  -> backend.agents.judge.run_judge()
  -> verify_claim() response_payload["evidence"]
  -> React evidence cards
```

## Stage trace

| Stage | Input | Output | Used? | Ignored or stale? |
|---|---|---|---|---|
| `verify_claim` | `ClaimRequest.claim` | normalized claim and model prediction | Yes | No |
| `decompose_claim` | normalized claim | sub-claim list | Yes | Before the fix, every `and` was incorrectly treated as a separator |
| `_retriever_node` | claim, analyzer keywords/domain, DistilBERT prediction | evidence and retrieval metadata | Yes | No |
| `retrieve_evidence_minimal` | claim and query variants | provider results or local fallback | Yes | Fallback was the failure path |
| `search_tavily` | generated query | normalized Tavily articles and metadata | Yes in fresh process | Empty in stale process |
| `_search_newsapi` | generated query | normalized NewsAPI articles and metadata | Yes in fresh process | Empty in stale process |
| `_search_serpapi` | generated query | normalized SerpAPI articles | No results because no SerpAPI key | Not used for successful evidence |
| FAISS branch | candidate articles | in-memory similarity ranking | No | Disabled because `VERITAS_USE_ADVANCED_RAG=0` |
| prosecutor/defender | filtered evidence | arguments and strengths | Yes | No |
| judge | claim, arguments, evidence | verdict/confidence/reasoning | Yes | DistilBERT is not passed directly to judge |
| response serialization | `top_results` | JSON `evidence` list | Yes | No |

## Evidence origin

The UI evidence originates in `backend.main.verify_claim()`:

1. `graph_result = run_claim_graph(...)`
2. `evidence_rows = graph_result["evidence"]`
3. `analysis_pool` normalizes those rows.
4. `top_results = analysis_pool[:5]`
5. `response_payload["evidence"]` serializes `top_results`.

The graph evidence originates in `backend.agents._retriever_node()`, which
calls `backend.rag.retriever.retrieve_evidence()`.

## Tavily

Tavily is called by `backend.rag.retriever._gather_from_providers()`:

```python
tav_articles, tav_meta = search_tavily(query, top_n=top_n)
```

The exact request is made by `backend.rag.tavily_client.search_tavily()` through
the Tavily SDK:

```python
client.search(
    query=query,
    search_depth=TAVILY_SEARCH_DEPTH,
    max_results=max(1, int(top_n)),
    include_raw_content=bool(include_raw),
    include_answer=False,
)
```

In the failing stale process, every Tavily response was empty with
`TAVILY_API_KEY missing or disabled`.

In a fresh process, Tavily returned non-empty results. For example, the Earth
claim returned five results for each of the generated queries, including NASA
and Britannica sources.

## NewsAPI

NewsAPI is called by
`backend.rag.retriever._gather_from_providers()` through
`_search_newsapi()`, using:

```text
GET https://newsapi.org/v2/everything
```

with `q`, `language=en`, `sortBy=relevancy`, `pageSize`, `apiKey`, and a trusted
domain filter on the first attempt.

For the fresh Earth-claim trace:

- trusted-domain request: HTTP 200, 0 parsed articles
- unrestricted request: HTTP 200, 5 parsed articles

In the stale process, NewsAPI was never called because its imported key was
empty, so its response list was empty.

## Local fallback and FAISS

The fallback file is:

`backend/data/news_articles.json`

It contains seeded documents including the observed Reuters World War 3 item
and Hindu Business Line gold-price item. This file is loaded by
`_load_local_fallback()` only when all provider results are empty.

FAISS exists in:

- `backend/rag/faiss_store.py`
- `backend/legacy_rag_core.py`
- `backend/rag/retriever.py`

The active request path did not use a persisted FAISS index. The advanced
branch creates an in-memory `FaissStore` from the current request's documents,
but `VERITAS_USE_ADVANCED_RAG=0` selects the minimal path.

## Cache audit

Relevant cache/history surfaces found:

- `backend/rag/retriever.py`: in-memory `_API_CACHE`, disabled by default when
  `VERITAS_DISABLE_ADVANCED_CACHE` is not set to `0`
- `backend/database.py`: SQLite `claim_cache`, bypassed because
  `backend.main.ENABLE_ADVANCED_CACHE = False`
- `backend/services/cache_service.py`: response metadata helper
- `backend/database.py`: claim history persistence
- FAISS/in-memory stores described above

The failing response was not a stale API-cache hit. Its metadata showed
`fallback_used=true` and provider counts of zero.

## Hardcoded phrase audit

| Phrase | File |
|---|---|
| `World War 3` | `backend/main.py` |
| `World War 3` | `backend/data/news_articles.json` |
| `Gold prices` | `backend/data/news_articles.json` |
| `3900` | `backend/data/news_articles.json` |
| `Hindu Business Line` | `backend/data/news_articles.json` |
| `Reuters` | `backend/data/news_articles.json` |
| `Reuters` | `backend/agents/judge.py` recommendation text |
| Related archived references | `archive/backend/rag/knowledge_base.py`, `archive/backend/legacy/legacy/rag/evidence_retriever.py` |

The observed titles were therefore real seeded fallback documents, not
Gemini-generated text.

## DistilBERT influence

DistilBERT is produced in `backend.main._model_prediction()`, which calls
`get_model_service().predict(text)`.

The prediction is:

- returned to the frontend as `model_prediction`
- passed into `run_claim_graph()`
- used by the retriever to add a classification-context query

It is not passed directly into `run_judge()`. Therefore it influences
retrieval context but does not directly determine the final judge verdict.

## Fresh-process verification

After restarting with the corrected backend-local environment loading, provider
counts were non-zero and `fallback_used` was false:

| Claim | Search query family | Retrieved sources | Verdict | Evidence titles | Confidence |
|---|---|---|---|---|---:|
| The Earth revolves around the Sun. | Earth/orbit/fact-check variants | Tavily 30, NewsAPI 12 | TRUE | NASA Science, Facts About Earth, Sun: Facts | 97 |
| Lions have tails. | Lions/tails variants | Tavily 30, NewsAPI 1 | FALSE/INSUFFICIENT_DATA across stale and fresh test processes | Mountain Lion Foundation, FELIDA, PBS | 57-78 |
| India and Pakistan fought wars. | India/Pakistan/wars variants after the fix | Tavily 30, NewsAPI 2 | FALSE in the fresh run | Britannica India-Pakistan conflict, TechPolicy.Press | 71 |
| The moon is made of cheese. | Moon/cheese/fact-check variants | Tavily 30, NewsAPI 21 | FALSE | Mental Floss, EnWave | 99 |

The required conjunction bug was fixed in `backend/agents.py`: factual claims
are no longer split on every `and`, preserving entities such as
“India and Pakistan” in the retrieval query.

The remaining Lions and India verdict discrepancies occur after relevant
evidence reaches the agents and are separate judge/stance-quality issues, not
the repeated-evidence root cause. No additional judge rewrite was made.

## Files changed

- `backend/llm_client.py` — explicit backend-local dotenv loading from the
  environment-loading fix
- `backend/rag/tavily_client.py` — explicit backend-local dotenv loading from
  the environment-loading fix
- `backend/agents.py` — preserve conjunctions in factual claims
- `ENVIRONMENT_FIX_REPORT.md` — environment-loading verification
- `RETRIEVAL_TRACE_REPORT.md` — this trace

No temporary debug statements were added. Existing runtime logs were used for
the trace and no UI or API route was changed.
