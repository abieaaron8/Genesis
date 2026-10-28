# Database and Storage

## Connection

`backend/database.py` reads `DATABASE_URL`, defaulting to `sqlite:///./genesis.db`. Because the path is relative, the working directory determines which file is used. The repository currently contains root and backend database files; choose one explicit deployment working directory before production.

## Tables

| Table | Columns and purpose |
|---|---|
| `users` | `id`, unique `username`, unique `email`, password hash, creation time, active flag |
| `claim_history` | User-linked claim, verdict, confidence, domain, timestamp, short share ID, bookmark flag, serialized details |
| `claim_cache` | Claim hash, JSON result, creation time |
| `claims` | Compatibility table with cache/hash/short-ID columns; not represented by an ORM class |

`User.claims` and `ClaimHistory.user` form the ORM relationship. `claim_history.user_id` is nullable so guest verification is possible.

## Lifecycle

Startup calls `init_db()`, creates missing tables, and applies SQLite compatibility columns. Verification saves a full result snapshot for authenticated users. History endpoints read ORM rows and deserialize `details_json`. Cache helpers use direct SQLite SQL and are separate from the main ORM session.

## Indexes and constraints

Users index and constrain username/email. Primary keys index IDs. `short_id` is unique when present. Claim hashes identify cache entries. Foreign-key ownership and authorization checks should be strengthened before public deployment.

## Storage notes

Frontend LocalStorage caches recent successful results for a limited time and stores the `genesis-token`. This client cache is independent from backend claim caching, which is disabled in the active main configuration.
