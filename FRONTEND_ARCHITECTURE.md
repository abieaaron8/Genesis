# Frontend Architecture

## Application shell

`src/main.jsx` mounts React under `StrictMode` and `BrowserRouter`. `src/App.jsx` defines routes, restores the Genesis JWT from local storage, loads the current user, applies theme state, and provides logout behavior.

## Routes

| Route | Component | Purpose |
|---|---|---|
| `/` | `Home.jsx` | Claim entry and verification workspace |
| `/history` | `History.jsx` | Stored verification list and details |
| `/stats` | `Stats.jsx` | Chart.js statistics view |
| `/login` | `Login.jsx` | Authentication |
| `/register` | `Register.jsx` | Account creation |
| `/profile` | `Profile.jsx` | Current-user settings |
| `*` | Redirect | Returns to home |

## Reusable components

`EvidenceCard`, `AgentCard`, `ConfidenceGauge`, `PipelineProgress`, `SkeletonCard`, and `VerdictBadge` keep result presentation modular. `src/services/api.js` centralizes Axios calls, base URL selection, bearer token attachment, and PDF fallback behavior.

## State and hooks

State is local React state rather than Redux or a global store. `Home.jsx` owns claim, loading, error, result, history, and sidebar/workspace state. Effects bootstrap history and session-dependent data. Successful verification results are cached in LocalStorage for a limited period.

## Styling and assets

Global and application styles live in `App.css` and `index.css`; authentication-specific styles live in `pages/AuthSplit.css`. Icons come from Lucide React. Framer Motion is used for restrained transitions. Vite serves `public` assets and produces `dist`.

## Performance

The client avoids unnecessary global state and lazy-loads no routes currently. The main performance risks are a large JavaScript chunk, chart dependencies loaded with the app, and repeated external verification latency. The build reports a chunk-size warning above 500 kB.
