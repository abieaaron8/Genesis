# Genesis frontend integration

## Architecture

The React application uses a single article-first verification workspace. The backend remains the source of truth for claims, evidence, model output, verdicts, confidence, history, and report exports.

```text
App shell
  ├─ navigation and authentication state
  ├─ / verify workspace
  │    ├─ claim composer
  │    ├─ backend stage timeline
  │    ├─ judge reasoning
  │    ├─ evidence list
  │    └─ verdict / model / source side rail
  ├─ /history
  ├─ /stats
  └─ auth and profile routes
```

## Component responsibilities

- `pages/Home.jsx` owns the verification interaction, result normalization, loading/error states, recent history, cached snapshots, and PDF export.
- `components/PipelineProgress.jsx` renders only the four stage statuses returned by `stages`: claim analysis, retrieval, agent reasoning, and verdict.
- `components/VerdictBadge.jsx` maps backend verdict values to semantic colors without changing the verdict.
- `components/ConfidenceGauge.jsx` visualizes the backend confidence value. It accepts both the API's percentage confidence and normalized values.
- `components/EvidenceCard.jsx` renders source, title, content, stance, credibility, publication date, recency, and source URL only when supplied.
- `components/AgentCard.jsx` renders the backend prosecutor/defender arguments and source counts without generating additional claims.
- `services/api.js` remains the only HTTP integration layer. Existing endpoints are used without backend changes.

## API integration

### Verification

`POST /api/verify`

Request:

```json
{ "claim": "A claim to verify" }
```

The UI consumes the returned:

- `claim`
- `domain`
- `claim_type`
- `evidence`
- `verdict`
- `confidence`
- `reasoning`
- `reasoning_points`
- `stages`
- `model_prediction`
- `evidence_summary`
- prosecutor and defender arguments
- history identifiers for PDF export

### History

- `GET /api/claims/history`
- `GET /api/claims/history/{historyId}`
- `DELETE /api/claims/{historyId}`

History is displayed only when returned by the backend. Recent claims are a compact navigation aid, not fabricated activity.

### Report export

The existing export fallback chain in `services/api.js` is preserved:

- `GET /api/export/pdf/{historyId}`
- fallback: `GET /api/claims/history/{historyId}/export`

### Authentication

Existing authentication calls and bearer-token behavior are unchanged:

- `POST /api/auth/login/`
- `POST /api/auth/register/`
- `GET /api/auth/me/`

## Design decisions

### Article-first hierarchy

The claim is treated as the primary document. Navigation is intentionally quiet, while the center column gives the claim, timeline, judge note, and evidence the most space.

### Editorial visual language

- Warm neutral paper background with a white reading surface.
- Newsreader for claim and verdict writing; DM Sans for interface controls and metadata.
- Hairline borders and restrained source accents instead of decorative cards or gradients.
- Green, red, and amber appear only for semantic verification states.
- Blue is reserved for active processing and links.

### Motion

Framer Motion is limited to result and status transitions. Loading uses a subtle skeleton and the timeline uses a small active-state rotation. `prefers-reduced-motion` disables non-essential movement.

### Missing data

The frontend does not synthesize statistics, charts, evidence, source ratings, or model output. Sections are omitted or reduced to a clear empty state when the corresponding backend field is unavailable.

### Accessibility

- Semantic `main`, `section`, `aside`, `article`, `header`, and `nav` landmarks.
- Visible keyboard focus styles.
- Labels and `aria-live` behavior for claim submission and errors.
- Source links open in a separate tab with `rel="noreferrer"`.
- Responsive layout collapses the side rail while retaining the same information order.

## Responsive behavior

- Desktop: left workspace rail, article-first center column, sticky verification rail.
- Tablet: compact navigation and narrower two-column verification layout.
- Mobile: navigation rail becomes hidden, the verification rail moves below the article, and argument/evidence sections become single-column.

## Data integrity

The UI does not alter backend verdict semantics or inference results. It normalizes absent fields to safe empty values for rendering, but it never fills them with invented content. Cached results are explicitly labeled as recent snapshots when a refresh fails.
