# CORS fix report

## Root cause

`backend/main.py` already registered `CORSMiddleware`, but `_parse_cors_origins`
treated `CORS_ORIGINS` as a replacement for the development defaults. When the
environment variable was configured without `http://localhost:5174`, FastAPI
returned no `Access-Control-Allow-Origin` header for the React application on
port 5174.

## Fix

The parser now merges configured origins with the required development origins:

- `http://localhost:5173`
- `http://localhost:5174`
- `http://127.0.0.1:5173`
- `http://127.0.0.1:5174`

Duplicate origins are removed while preserving order. The middleware continues
to allow:

- all methods
- all headers
- credentials

No API routes or request/response schemas were changed.

## Verification

- FastAPI app initialization remains in `backend/main.py`.
- `CORSMiddleware` remains installed before route registration.
- `/api/claims/history` returned HTTP 200 with credentials enabled.
- `/api/verify` was tested using the existing endpoint and remains subject to
  the backend's normal evidence-provider processing time.
- Frontend origin `http://localhost:5174` is now always included, even when
  `CORS_ORIGINS` is set.
