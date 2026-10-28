# Genesis Presentation Notes

Generated from the active repository implementation. Replace Slide 10 placeholders with runtime screenshots before public delivery.

## Slide 1 — Problem Statement

Say: Genesis addresses a practical problem: claims spread faster than careful verification. The system is designed as an evidence-oriented workflow, not a single black-box label. It combines local machine learning with source retrieval, structured reasoning, and a user-facing explanation.

Emphasize: the project is implemented as a full-stack system—React in the browser, FastAPI in Python, a DistilBERT artifact for local inference, retrieval providers, agent stages, and SQLite persistence.

Likely viva questions: Why not use only an LLM? Answer: the classifier and retrieval provide separate signals, while the pipeline exposes evidence and reasoning. Is it a perfect truth engine? No; provider coverage, source quality, and model limitations remain important.

## Slide 2 — Proposed Solution

Say: The core product idea is a chain of accountable steps. The input is not immediately turned into a verdict. Genesis first gathers context, then reasons over evidence, and finally returns both a decision and the material used to support it.

Emphasize: the output is structured. The frontend receives evidence, arguments, confidence, reasoning, pipeline stages, and the model signal rather than only a label.

Likely question: What happens when evidence is unavailable? The retriever can fall through providers or use the local fallback path, and the judge can return UNVERIFIED or INSUFFICIENT_DATA rather than pretending certainty.

## Slide 3 — System Architecture

Say: This is the runtime architecture. The browser calls a FastAPI composition root. The backend combines the local classifier, claim orchestration, retrieval providers, debate stages, and storage. Optional LLM providers are behind feature flags and fallback logic.

Emphasize: Neo4j and advanced FAISS retrieval exist in the repository but are disabled by the active defaults. That distinction matters when describing the project accurately.

Likely question: Where is the main integration point? backend/main.py, especially verify_claim(), startup configuration, and the route definitions.

## Slide 4 — Technology Stack

Say: The stack is deliberately modular. React handles the investigation workspace, FastAPI owns the API and orchestration, PyTorch and Transformers serve the local classifier, and retrieval/LLM providers contribute fresh context and optional reasoning.

Emphasize: the dependency list is not a claim that every optional integration is active in every run. The defaults use minimal retrieval and deterministic agent logic unless feature flags are enabled.

Likely question: Why keep both FAISS and SQLite? SQLite stores application records; FAISS is an in-memory vector search abstraction for the advanced retrieval path.

## Slide 5 — AI Verification Pipeline

Say: This is the most important technical slide. Genesis does not collapse all intelligence into one model. It validates and decomposes the claim, retrieves sources, ranks them, classifies support and contradiction, runs prosecutor and defender roles, then lets the judge and verdict hardening produce the final response.

Emphasize: the local classifier is advisory. It is not the sole decision-maker and a model failure is designed to be non-fatal.

Likely question: What is RAG here? Retrieval-Augmented Generation means evidence is gathered first and then supplied as context to reasoning stages; the source records remain part of the result.

## Slide 6 — Features

Say: Genesis is more than a model endpoint. The active product includes a claim workspace, evidence cards, confidence display, staged progress, agent reasoning, history, authentication, statistics, and PDF export.

Emphasize: the list deliberately avoids unsupported claims such as streaming verification, a production browser extension, or an active knowledge graph. Those are future work, not current features.

Likely question: Are bookmarks complete? The database has a bookmarked field, but the active route surface should be treated as the source of truth for supported user actions.

## Slide 7 — Machine Learning and AI

Say: Genesis uses several distinct AI techniques. DistilBERT is trained for binary fake-news classification. RAG brings in current evidence. Optional LLM providers can reason over structured context. Deterministic agents and rules provide predictable fallbacks and post-processing.

Emphasize limitations: WELFake is not a complete representation of current events, provider responses can be empty or stale, and LLM output must be constrained by retrieved evidence.

Likely question: Why include rules if there is a neural model? Rules improve determinism for known cases and help validate or harden outputs, but they also create maintenance debt and should be audited.

## Slide 8 — Live Project Workflow

Say: This is the live demo narrative. The user clicks Verify claim. React enters loading state and Axios posts the claim. FastAPI obtains the singleton model signal, executes the graph and retrieval path, then returns a structured JSON payload. React clears loading in finally and renders the result.

Emphasize: first requests can be slower because model and embedding resources are lazy-loaded, while external search and optional LLM calls add latency.

Likely question: How is failure handled? Model errors can be non-fatal; provider errors can fall through; FastAPI validation produces 4xx responses; the frontend surfaces errors and always clears the loading state.

## Slide 9 — Course Outcomes

Say: This mapping is based on actual modules rather than generic AI vocabulary. CO1 is supported by the analyzer, prosecutor, defender, judge, and graph runner. CO2 is represented by multiple search providers and ranking. CO3 is visible in the typed state, evidence records, ORM schema, and JSON context. CO4 is visible in confidence, credibility, disagreement, and conflicting evidence handling. CO5 is supported by the WELFake/DistilBERT training and inference code plus optional LLM integration.

Likely question: Is every search strategy active by default? No. The code includes minimal and advanced paths, and active defaults disable some advanced features.

## Slide 10 — User Interface Showcase

Say: The active frontend is a React investigation workspace. The main Home page contains the claim composer, loading pipeline, result timeline, evidence cards, reasoning, verdict, confidence gauge, and model signal. History, stats, authentication, and profile are separate routes.

Be transparent: the repository does not currently contain a maintained screenshot set for the active UI, so these frames are deliberate placeholders. Replace them with captured screens from the running app before presenting the deck as a visual product showcase.

Likely question: Which components are reusable? EvidenceCard, AgentCard, ConfidenceGauge, PipelineProgress, SkeletonCard, and VerdictBadge.

## Slide 11 — Future Improvements

Say: The roadmap is intentionally grounded in observed gaps. The first priorities are authentication reliability, ownership checks, deterministic database paths, provider mocks, and contract tests. Then the system can improve retrieval evaluation, model calibration, async performance, frontend bundle size, and deployment.

Emphasize: multilingual support, browser extension, mobile, streaming, and knowledge graph expansion are future directions—not current features.

Likely question: Which improvement has the highest impact? Reliable auth and authorization, followed by evidence evaluation and reproducible tests.

## Slide 12 — Conclusion

Say: Genesis brings together the major ideas in an applied AI system: a real frontend, a real backend, a locally loaded classifier, retrieval providers, structured agent stages, persistence, authentication, and explainable output.

Close with the impact: the system does not promise perfect truth; it gives users a more inspectable path from claim to evidence to confidence.

Likely final questions: What would you improve first? Authentication reliability and test coverage. What is the strongest technical learning? Integrating model inference, retrieval, API design, stateful UI, and operational configuration into one coherent product.
