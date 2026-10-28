# Flowcharts

## Overall architecture

```mermaid
flowchart TB
  User --> React
  React --> Axios
  Axios --> FastAPI
  FastAPI --> Model[DistilBERT]
  FastAPI --> Pipeline[Verification pipeline]
  Pipeline --> Retrieval
  Pipeline --> Agents[Analyzer / Prosecutor / Defender / Judge]
  FastAPI --> SQLite
  Pipeline --> Response
  Response --> React
```

## API flow

```mermaid
flowchart LR
  Request --> Validate[Pydantic validation]
  Validate --> Dependency[Auth and DB dependencies]
  Dependency --> Handler[Route handler]
  Handler --> JSON[JSON response]
```

## Verification pipeline

```mermaid
flowchart TD
  Claim --> Prediction
  Claim --> Decomposition
  Prediction --> State
  Decomposition --> State
  State --> Retrieval
  Retrieval --> Evidence
  Evidence --> Debate
  Debate --> Judge
  Judge --> Hardening
  Hardening --> Verdict
```

## Evidence retrieval

```mermaid
flowchart LR
  Query --> Tavily
  Query --> SerpAPI
  Query --> NewsAPI
  Query --> LocalFallback
  Tavily --> Normalize
  SerpAPI --> Normalize
  NewsAPI --> Normalize
  LocalFallback --> Normalize
  Normalize --> Filter --> Rank --> Context
```

## LLM reasoning

```mermaid
flowchart TD
  Context --> ProviderCheck
  ProviderCheck --> Groq
  ProviderCheck --> Gemini
  ProviderCheck --> Ollama
  Groq --> Parse
  Gemini --> Parse
  Ollama --> Parse
  Parse --> DeterministicFallback
  Parse --> JudgeOutput
```

## Database interactions

```mermaid
erDiagram
  USER ||--o{ CLAIM_HISTORY : owns
  CLAIM_HISTORY {
    int id PK
    int user_id FK
    string claim_text
    string verdict
    float confidence
    string details_json
  }
  CLAIM_CACHE {
    string claim_hash PK
    string result_json
    datetime created_at
  }
  CLAIMS {
    int id PK
    string claim_hash
    string cached_response
    string short_id
  }
```

## Frontend navigation

```mermaid
flowchart LR
  App --> Home
  App --> History
  App --> Stats
  App --> Login
  App --> Register
  App --> Profile
  Unknown --> Home
```

## Folder hierarchy

```mermaid
graph TD
  Root --> Backend
  Root --> Frontend
  Root --> Data
  Root --> Archive
  Backend --> RAG
  Backend --> Services
  Backend --> Agents
  Backend --> Training
  Frontend --> Pages
  Frontend --> Components
  Frontend --> APIClient
```

## Component dependency graph

```mermaid
graph TD
  Home --> APIClient
  Home --> PipelineProgress
  Home --> EvidenceCard
  Home --> AgentCard
  Home --> ConfidenceGauge
  Home --> VerdictBadge
  History --> APIClient
  Stats --> APIClient
  Login --> APIClient
  Register --> APIClient
  Profile --> APIClient
```
