# Genesis Verification Pipeline Architecture

## Purpose

Genesis combines a local DistilBERT fake-news classifier with evidence retrieval and a multi-stage claim analysis workflow. The classifier is advisory context for retrieval and reasoning; it does not replace source-backed verification.

## End-to-end flow

```text
User claim
   |
   v
DistilBERT model service
   |  prediction, confidence, class probabilities
   v
Claim analyzer
   |  claim type, domain, keywords, sub-claims
   v
Query builder
   |  original claim + ML prediction context
   v
Evidence retrieval
   |  Tavily / SerpAPI / NewsAPI / curated or local fallback
   v
Evidence normalization and filtering
   |  deduplication, relevance, source validation
   v
Hybrid ranking
   |  semantic similarity + keyword relevance + credibility + recency
   v
Evidence classifier
   |  SUPPORTS / CONTRADICTS / NEUTRAL
   v
Prosecutor and Defender
   |  evidence-grounded arguments only
   v
Judge
   |  verdict, confidence, reasoning, key evidence
   v
FastAPI response
```

## Stage responsibilities

1. **Model service** lazily loads the saved tokenizer and DistilBERT checkpoint once, using CUDA when available and CPU otherwise. Loading is protected by a thread-safe singleton.
2. **Claim analysis** extracts the claim type, domain, keywords, and decomposition needed by retrieval.
3. **ML-aware query generation** always preserves the original claim and adds a classification-context query such as `real/fake news classification fact check evidence`.
4. **Retrieval** queries configured providers and uses deterministic fallback sources when providers are unavailable. Evidence is retained with source, URL, publication date, and retrieval metadata.
5. **Filtering** removes duplicates and low-relevance or malformed records. The system does not invent citations or evidence.
6. **Ranking** records `embedding_score`, `credibility_score`, `recency_score`, and `final_score`. The final score combines semantic relevance, keyword overlap, source credibility, and freshness.
7. **Evidence classification** labels evidence as supporting, contradicting, or neutral relative to the claim.
8. **Argument agents** receive only retrieved evidence and produce bounded arguments. If no evidence exists, deterministic no-evidence responses are used.
9. **Judge synthesis** compares the evidence-backed arguments and returns a normalized verdict, confidence, explanation, and evidence counts.
10. **API serialization** preserves the existing `/api/verify` contract and adds `model_prediction`, optional model errors, and `evidence_summary`.

## Reliability and safety

- Model inference is local-only and does not download artifacts at request time.
- Provider failures are logged and handled through the existing fallback chain.
- Empty evidence never triggers fabricated citations.
- Stage failures include the failed stage and error details in the pipeline response.
- Logging identifies claim analysis, ML-aware retrieval, filtering, arguments, judging, and response serialization.
- Existing `/api/verify` behavior remains available; `/api/model/predict` exposes the classifier independently.

## Output contract

The verification response includes:

- `verdict`
- `confidence`
- `reasoning` and `reasoning_points`
- `evidence_summary`
- supporting and contradicting counts
- `model_prediction`
- stage and retrieval metadata
