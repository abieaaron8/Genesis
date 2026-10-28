# Frontend verification loading debug report

## Result

The verification flow now completes successfully in the browser. A live browser
request sent:

```text
POST http://localhost:8000/api/verify
```

The request returned HTTP 200 in approximately 19 seconds and rendered the
verdict, confidence, model signal, reasoning, evidence, and related sources.
The button returned from `Checking…` to `Verify claim`.

## Root cause

The React click handler and Axios request were functioning correctly. The
apparent infinite loading state was caused by the backend verification request
taking a long time when external evidence providers were unavailable or had
invalid credentials:

- Tavily was skipped because its key was unavailable.
- SerpAPI returned invalid-key responses.
- NewsAPI returned invalid-key responses.
- The retrieval path performed multiple provider/query attempts before the
  backend could serialize a response.

The frontend Axios client had a five-minute timeout, so a request in that
provider-failure path looked like a permanently stuck `Checking…` state.

During tracing, the backend also logged an `OSError` from a debug
`print(json.dumps(response_payload, indent=2))` call. That stdout dump was
removed and replaced with structured debug logging. The response schema and
endpoint were not changed.

## Flow trace

1. `Home.jsx` button calls `runVerification(claim)`.
2. `runVerification` trims the claim, clears prior errors, sets `loading=true`,
   and awaits `verifyClaim`.
3. `services/api.js` sends Axios `POST /api/verify` to the configured
   `VITE_API_BASE_URL` (`http://localhost:8000` in local development).
4. FastAPI receives the request and runs the existing verification pipeline.
5. Axios resolves with the backend JSON response.
6. `normalizeVerificationResult` maps the existing backend fields without
   inventing values.
7. React stores the result and renders the timeline, verdict, evidence,
   reasoning, model prediction, and confidence.
8. The `finally` block always sets `loading=false`.

## Browser and network verification

- Frontend loaded at `http://localhost:5173`.
- Backend OpenAPI loaded at `http://127.0.0.1:8000/openapi.json`.
- Button click changed the label to `Checking…`.
- Browser network timing showed:
  `http://localhost:8000/api/verify` — HTTP 200, approximately 19 seconds.
- The rendered page showed `FALSE`, `98% confidence`, `FAKE` DistilBERT output,
  two evidence sources, judge reasoning, and source links.
- No visible runtime error was present after the successful response.
- The final button label was `Verify claim`, confirming loading completion.

## Files changed

### `frontend/react-app/src/pages/Home.jsx`

- Preserved the existing async flow and `finally` cleanup.
- Added an explicit user-facing message for Axios timeout errors.
- Kept response normalization aligned with the current backend response fields.

### `frontend/react-app/src/services/api.js`

- Reduced the Axios timeout from 300 seconds to 60 seconds so unavailable
  provider paths fail visibly instead of appearing infinite.
- The request URL and endpoint remain unchanged: `POST /api/verify`.

### `backend/main.py`

- Replaced the response-payload stdout dump with `logger.debug`.
- Replaced exception-path stdout prints with structured logging.
- No endpoint, request schema, response schema, or application behavior was
  intentionally changed.

## Validation

- Frontend production build: passed.
- Frontend lint: passed with one existing warning in `Profile.jsx` about an
  unnecessary `useMemo` dependency; no errors.
- Live backend verification: HTTP 200 with verdict and confidence.
- Browser verification: result rendered and loading completed.

## Why this fixes the issue

Successful requests continue to render the complete backend response exactly as
before. If external providers cause the backend request to exceed the bounded
client wait, Axios now rejects and `Home.jsx` displays a clear timeout message;
its `finally` block returns the UI to the non-loading state. This prevents the
interface from remaining indefinitely in `Checking…` without inventing a
verdict or changing backend APIs.
