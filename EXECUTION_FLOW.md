# Execution Flow

## From “Verify Claim” to visible result

1. `Home.jsx` validates that the claim is non-empty and sets loading state.
2. `verifyClaim()` in `src/services/api.js` sends `POST /api/verify` through Axios.
3. FastAPI validates the request model and enters `verify_claim()` in `backend/main.py`.
4. `_model_prediction()` obtains the lazy singleton DistilBERT signal.
5. The route checks optional authentication and known-fact shortcuts.
6. `decompose_claim()` and `run_claim_graph()` build the verification state.
7. Retrieval searches configured providers, normalizes documents, filters duplicates, and ranks evidence.
8. Prosecutor and defender classify evidence stance and write arguments.
9. Judge synthesis and post-processing determine verdict, confidence, explanation, and evidence summary.
10. Authenticated results are persisted in `claim_history` with a serialized `details_json` snapshot.
11. FastAPI returns JSON.
12. React normalizes response fields, updates result state, stops loading in `finally`, and renders timeline, evidence, reasoning, and verdict components.

## Pseudocode

```python
def verify_claim(request):
    model_signal = model_service.predict(request.claim)
    state = decompose_claim(request.claim, model_signal)
    state = run_claim_graph(state)
    result = reconcile_and_harden(state, model_signal)
    if current_user:
        save_history(result)
    return result
```

## Error flow

Provider failures are logged and can fall through to another provider or the local dataset. Model-service failure is returned as a non-fatal model error when possible. FastAPI validation failures become 4xx responses. React catches Axios failures, presents an error state, and clears loading regardless of success or failure.

## Timing

The slowest stages are external search, raw-content extraction, embedding initialization, LLM calls, and model initialization on the first request. DistilBERT and embedding models are lazy-loaded; the first request can be materially slower than subsequent requests.

## Call stack

`Home.handleVerify` → `verifyClaim` → `POST /api/verify` → `main.verify_claim` → `_model_prediction` → `get_model_service().predict` → `decompose_claim` → `run_claim_graph` → retrieval/agent nodes → verdict hardening → database save → Axios response → React state update.
