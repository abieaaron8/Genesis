# LLM Integration

## Providers and order

`backend/llm_client.py` supports:

1. Groq when `GROQ_API_KEY` is configured.
2. Gemini when `GEMINI_API_KEY` is configured.
3. Ollama as a local fallback unless disabled.

DeepSeek variables exist in examples and historical material, but the active `call_reasoning()` path does not currently establish DeepSeek as a provider.

## Configuration

Provider keys are loaded from `backend/.env` using `python-dotenv`. Model names, base URLs, cooldowns, and disable flags are read from environment variables. Values must never be logged.

## Reasoning flow

Optional analyzer, evidence-classifier, prosecutor, defender, and judge calls are controlled independently by feature switches. Structured JSON extraction is handled by `extract_json()`. If a provider fails, the client can try the next provider or return a deterministic fallback path.

## Prompt boundary

The active code constructs prompts around the claim, normalized evidence, and role-specific instructions. The judge receives evidence and agent arguments; it is not intended to invent sources. Provider output is parsed and then reconciled by backend hardening logic.

## Temperature and models

The exact provider model and generation parameters are configuration-driven and should be read from the active `llm_client.py` and environment file rather than assumed from archived documentation. `GROQ_JUDGE_MODEL`, `GEMINI_MODEL`, and Ollama model variables are the primary discovered controls.

## Operational guidance

Use deterministic mode for local tests. Enable one provider at a time when debugging. Check `/api/health`, provider logs, timeout behavior, and fallback outputs. Do not treat an LLM-ready health signal as proof that evidence quality is correct.
