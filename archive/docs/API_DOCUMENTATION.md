# API Documentation

The active API is defined in `backend/main.py`. OpenAPI is available at `/openapi.json` and Swagger UI at `/docs`.

## Verification

### `POST /api/verify`

Runs the full pipeline. Body is a claim request containing the claim text and optional frontend fields accepted by the current Pydantic model. Validation rejects malformed/empty input. The response includes verdict, confidence, explanation/reasoning, evidence, evidence summary, model prediction, pipeline stages, and agent analyses. Authenticated requests save history; guest verification remains supported.

### `POST /api/model/predict`

Runs only the DistilBERT model service. Returns prediction/label, confidence, class probabilities, and device. Model artifacts are loaded lazily and once per process.

### `POST /api/verify/batch`

Accepts up to five claims and verifies them concurrently through the verification flow. Request parsing and count limits are implemented in `main.py`.

### `POST /api/verify/quick`

Compatibility route delegating to the primary verification implementation.

## History and reports

| Route | Behavior |
|---|---|
| `GET /api/claims/history` | Returns authenticated user history when a valid bearer token exists; otherwise a limited guest/recent view. Supports `limit`. |
| `GET /api/claims/history/{history_id}` | Returns a stored verification snapshot. |
| `GET\|HEAD /api/export/pdf/{verification_id}` | Generates a ReportLab PDF using numeric or short verification identifiers. |
| `GET\|HEAD /api/claims/history/{history_id}/export` | Alternate history PDF export. |
| `GET /api/share/{short_id}` | Returns a shareable stored verdict by short ID. |

## Analytics and system

| Route | Behavior |
|---|---|
| `GET /api/stats` | Returns global or user-scoped counts/statistics. |
| `GET /api/trending` | Returns top claims from the recent period. |
| `GET /api/health` | Reports application/provider readiness. The current source has a `grok`/`groq` key mismatch worth fixing. |
| `GET /api/sources` | Currently returns an empty list in active code. |

## Authentication

| Route | Behavior |
|---|---|
| `GET /api/auth/check-username` | Checks username availability. |
| `GET /api/auth/check-email` | Checks email availability. |
| `POST /api/auth/register` and `/register/` | Creates a user and returns authentication data on success. |
| `POST /api/auth/login` and `/login/` | Authenticates credentials and returns a JWT. |
| `GET /api/auth/me` and `/me/` | Returns the current bearer-authenticated user. |

## Error behavior

FastAPI validation errors use 422. Authentication failures use 401. Resource-not-found cases use 404. Provider/model failures are handled inside the pipeline where possible and represented in structured result fields or fallback behavior. Always inspect the response body rather than assuming HTTP 200 means evidence quality is good.

## Example

```powershell
$body = @{ claim = 'The Earth revolves around the Sun.' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/verify `
  -ContentType 'application/json' -Body $body
```

The exact accepted request/response fields should be treated as the generated OpenAPI contract, because the route preserves compatibility aliases for earlier frontend shapes.
