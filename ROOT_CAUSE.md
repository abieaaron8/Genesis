# Verify Claim: Root Cause

## First failure

- **File:** `backend/main.py`
- **Function:** `verify_claim`
- **Original line:** 2193
- **Failing call:** `print(json.dumps(response_payload, indent=2))`
- **Exception:** `OSError: [Errno 22] Invalid argument`

`veritas_debug.log` records the request reaching `"[PIPELINE] Response
serialization started"`, then raising this exception at the diagnostic
`print`. The response payload had been built, but the exception interrupted
the handler before `_save_history(...)` and `return response_payload`.

This is not an Axios, CORS, endpoint-registration, timeout, or deadlock
failure. Axios was waiting for the endpoint response that the exception
prevented the handler from returning.

## Request trace

1. `frontend/react-app/src/pages/Home.jsx` — `runVerification()` calls
   `verifyClaim(text)` and clears `loading` in its `finally` block.
2. `frontend/react-app/src/services/api.js` — `verifyClaim()` calls
   `api.post("/api/verify", { claim })`.
3. `backend/main.py` — `POST /api/verify` enters `verify_claim()`.
4. `verify_claim()` calls `decompose_claim()`, then `run_claim_graph()`.
5. The graph performs claim analysis, evidence retrieval, prosecutor,
   defender, and judge steps, then returns to `verify_claim()`.
6. `verify_claim()` constructs `response_payload`; the diagnostic `print` was
   the first failing operation.

## Minimal fix

The unsafe payload print was replaced with a normal logger call:

```python
logger.debug("[PIPELINE] Response payload validated for claim=%r", claim)
```

No request contract, UI flow, pipeline logic, or timeout value was changed as
part of this fix.

## Verification

- `POST http://127.0.0.1:8000/api/verify` with
  `{"claim":"The sun is rectangular"}` returned **200**.
- The response included a full result payload and `history_id`.
- The React production build completed successfully with `npm run build`.
- In the running React app, submitting the same claim displayed **Claim under
  review**, the **UNVERIFIED** result, reasoning, and confidence; the button
  returned from **Checking…** to **Verify claim**, confirming that loading
  ended.

The returned verdict is `UNVERIFIED` because configured evidence-provider
credentials are unavailable; that is the expected application result for this
request and is independent of the failed frontend submission.
