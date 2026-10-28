# Timeout Fix Report

## Status

The verification timeout was caused by blocking retrieval work accumulating across
providers and query variants. The active minimal retriever called Tavily, SerpAPI,
and NewsAPI sequentially. NewsAPI could then spend multiple attempts handling a
rate-limit response or a slow request, while the frontend Axios request had a
60-second limit.

The fix keeps the existing verification architecture and changes only retrieval
failure isolation:

- Tavily, SerpAPI, and NewsAPI now run concurrently for each query.
- Each provider has an 8-second wall-clock guard by default.
- A provider timeout or exception returns no results and does not abort retrieval.
- HTTP 429 responses are returned immediately instead of being retried.
- Existing provider timing and continuation logs are retained.

## Execution trace

| Stage | File and function | Responsibility |
|---|---|---|
| Client request | `frontend/react-app/src/services/api.js` | Sends `POST /api/verify` with a 60-second Axios timeout. |
| API endpoint | `backend/main.py:1628` `verify_claim` | Validates the request, runs inference and orchestration, then serializes the response. |
| Claim decomposition | `backend/agents.py:869` `decompose_claim` | Produces sub-claims/query context. |
| Graph entry | `backend/agents.py` `run_claim_graph` | Runs the analyzer, retriever, prosecutor, defender, and judge stages. |
| Retrieval node | `backend/agents.py:217` `_retriever_node` | Calls evidence retrieval and records evidence for downstream agents. |
| Minimal retrieval | `backend/rag/retriever.py:1722` `retrieve_evidence_minimal` | Tries the configured query variants and merges provider results. |
| Provider gather | `backend/rag/retriever.py:1304` `_gather_from_providers` | Runs Tavily, SerpAPI, and NewsAPI concurrently and merges their results. |
| Provider guard | `backend/rag/retriever.py:1240` `_run_provider_with_timeout` | Enforces the provider wall-clock limit and converts failures to empty results. |
| HTTP retry helper | `backend/rag/retriever.py:215` `_retry_request` | Performs provider HTTP requests; 429 responses now skip retries. |
| Evidence enrichment | `backend/rag/retriever.py:1676` `_enrich_full_content` | Optionally fetches article content after retrieval. |
| Prosecutor | `backend/agents.py:448` `_prosecutor_node` | Generates contradiction analysis from retrieved evidence. |
| Defender | `backend/agents.py:537` `_defender_node` | Generates supporting analysis from retrieved evidence. |
| Judge | `backend/agents.py:626` `_judge_node` | Produces the final evidence-based decision. |
| Response | `backend/main.py:1628` `verify_claim` | Returns the verdict, confidence, evidence, and analysis to the frontend. |

## Root cause

The timeout was backend-side and not a React rendering issue. The frontend
allowed 60 seconds, but retrieval previously accumulated provider latency:

1. Providers were called sequentially.
2. The minimal retriever used multiple query variants.
3. NewsAPI could retry HTTP 429 responses and slow requests.
4. The provider timeout wrapper limited an individual call, but sequential
   provider/query execution still allowed the total request to approach or exceed
   the frontend boundary.

The affected code path was `backend/rag/retriever.py`, specifically
`_gather_from_providers`, `_run_provider_with_timeout`, and `_retry_request`.
No frontend, model, judge, evidence-scoring, or UI code was changed.

## Provider credentials

Runtime presence checks were performed without printing secret values:

| Provider variable | Status |
|---|---|
| `NEWS_API_KEY` | Loaded |
| `NEWSAPI_KEY` | Missing; not required because `NEWS_API_KEY` is accepted |
| `TAVILY_API_KEY` | Loaded |
| `GEMINI_API_KEY` | Loaded |
| SerpAPI key | Missing; provider returns zero results and continues |

## Observed provider timings after the fix

Representative production-path logs showed providers starting together:

```text
[Retriever] Tavily started
[Retriever] SerpAPI started
[Retriever] NewsAPI started
[Retriever] SerpAPI finished (0.01 s, 0 results)
[Retriever] NewsAPI finished (2.27 s, 0 results)
[Retriever] Tavily finished (5.08 s, 10 results)
[Retriever] Total retrieval time: 7.35 s
```

Other query variants completed in approximately 6.1–8.7 seconds. A rate-limited
NewsAPI response no longer consumed additional retry attempts.

## Verification results

The backend was compiled with `python -m py_compile backend\rag\retriever.py`
and exercised through `POST http://127.0.0.1:8023/api/verify`.

| Claim | HTTP | Duration | Verdict | Supporting | Contradicting |
|---|---:|---:|---|---:|---:|
| NASA NEO Surveyor sunshade preparation | 200 | 32.97 s | MISLEADING | 4 | 0 |
| 3% Dearness Allowance announcement | 200 | 26.91 s | MISLEADING | 4 | 0 |
| Python is an interpreted programming language | 200 | 0.78 s | TRUE | 2 | 0 |

All three requests completed without the frontend 60-second timeout. Provider
failure isolation was confirmed: missing SerpAPI credentials and unavailable or
rate-limited NewsAPI results did not prevent Tavily evidence from reaching the
prosecutor, defender, and judge stages.

## Files modified

- `backend/rag/retriever.py`
  - Added concurrent provider execution.
  - Kept bounded provider timeout handling.
  - Reduced the default provider guard from 12 to 8 seconds.
  - Stopped retrying HTTP 429 responses.
- `TIMEOUT_FIX_REPORT.md`
  - Documents the trace, root cause, fix, timings, and validation.

## Scope preserved

The change does not modify the frontend, CSS, React components, DistilBERT,
training labels, evidence scoring, prosecutor/defender stance separation, judge
logic, API routes, or database behavior.
