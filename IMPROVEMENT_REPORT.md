# Improvement Report

This report distinguishes observed behavior from recommendations. It does not claim that archived or disabled paths are production-ready.

## Highest-impact findings

| Priority | Finding | Impact | Recommendation |
|---|---|---|---|
| P0 | Registration fails in the audited environment because Passlib 1.7.4 and Bcrypt 5.0.0 are incompatible | Authentication is not reliable | Pin a compatible bcrypt version or migrate to Argon2id; add registration/login tests |
| P0 | Relative SQLite URL can select different database files by working directory | History can appear to disappear or split | Resolve the path from a stable project/config directory and migrate deliberately |
| P0 | History detail/export ownership is not visibly enforced | Possible privacy exposure | Require current-user ownership or an explicit public-share token |
| P1 | Frontend calls `DELETE /api/claims/{id}` without an active matching route | Delete UI cannot work reliably | Add a documented route or remove/disable the client operation |
| P1 | `/api/health` reads `grok` while provider state uses `groq` | Health can misreport readiness | Align the key and add provider contract tests |
| P1 | Fallback/known-fact logic can dominate fresh evidence | Verdict behavior may be surprising | Make shortcuts explicit, auditable, and separately tested |
| P1 | LLM/search dependencies and documentation drift | Operators may enable unsupported assumptions | Generate docs from active config and remove stale provider claims |

## Architecture and performance

- External search and raw-content extraction are synchronous in a request path; use bounded async clients, timeouts, retries, and concurrency limits.
- First-request model and embedding initialization increases latency; preload in controlled deployments or expose warm-up status.
- A single large frontend chunk includes charting and UI dependencies; route-level code splitting would improve startup.
- SQLite is appropriate for local development but limits concurrent writes and horizontal scaling.
- Provider caches exist but default behavior is fragmented across frontend and backend.

## Security

- Replace the fallback JWT secret with a startup failure when `SECRET_KEY` is absent in production.
- Fix password-hashing dependency compatibility and migrate toward Argon2id.
- Enforce history ownership and validate share identifiers.
- Restrict CORS outside development.
- Add request size/rate limits and provider abuse controls.
- Treat retrieved text as hostile prompt input and preserve clear evidence boundaries.

## Maintainability

- `main.py` is a very large composition root; split route modules from application services.
- Compatibility wrappers (`rag_core.py`, `legacy_rag_core.py`, older predictor paths) make the active graph harder to follow.
- Duplicate aliases and fallback fields improve compatibility but should be covered by a versioned schema.
- Archive code should be clearly separated from active package discovery.

## AI and ML

- Add time-split and domain-specific evaluation, calibration, and drift monitoring for WELFake/DistilBERT.
- Measure retrieval precision/recall and source-quality agreement separately from final verdict accuracy.
- Replace hard-coded facts with versioned, cited knowledge or a reviewed ruleset.
- Add adversarial tests for prompt injection, misleading headlines, stale articles, and contradictory sources.
- Record evidence provenance and model/provider versions with each saved result.

## Testing and delivery

- Add backend unit tests, API contract tests, retrieval fixtures, auth tests, and browser-level verification tests.
- Add CI for compile, lint, frontend build, OpenAPI snapshot, and secret scanning.
- Provide an active Docker/production deployment configuration or explicitly document that deployment is not maintained.
- Pin compatible dependency ranges and use Dependabot/security scans.

## Recommended order

1. Fix authentication dependency compatibility and ownership authorization.
2. Make database location deterministic and migrate data safely.
3. Add deterministic provider mocks and end-to-end contract tests.
4. Split `main.py` and formalize response schemas.
5. Improve retrieval evaluation, model calibration, and provenance.
6. Optimize async I/O and frontend bundle loading.
7. Decide the long-term role of FAISS, Neo4j, archived providers, and Docker.
