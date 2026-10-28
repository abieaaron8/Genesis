# Project Overview

## What Genesis is

Genesis is a claim-verification application for investigating potentially false or misleading statements. A user submits a claim through a React workspace. FastAPI validates and orchestrates the request, DistilBERT supplies a local classification signal, retrieval providers collect candidate evidence, ranking and credibility utilities organize that evidence, and agent stages produce a verdict with confidence and explanation.

## Why it exists

The project makes verification more transparent than a single opaque label. It exposes evidence, source context, model output, and reasoning stages so a user can inspect how a result was formed.

## Who it helps

- Readers checking a claim before sharing it.
- Students learning how retrieval, classifiers, and LLM applications fit together.
- Engineers experimenting with evidence-aware AI systems.
- Judges and recruiters evaluating a complete AI product rather than an isolated model.

## Real-world use case

A user sees a political, health, science, or economic statement online. They paste it into Genesis, review retrieved sources and supporting/contradicting arguments, then use the verdict as a starting point for further human verification.

## Design philosophy

Genesis favors inspectability over magic: explicit pipeline stages, structured JSON, source-aware evidence, graceful provider fallback, and a quiet editorial frontend. The active runtime is conservative by default; optional LLM agents, advanced retrieval, caches, and Neo4j are feature-gated rather than assumed.

## Scope and limitations

Genesis does not prove truth in the philosophical sense. It depends on search coverage, source quality, current provider responses, a trained classifier, deterministic rules, and optional language models. Known-fact shortcuts exist in the active code and should be treated as production logic that requires continued review.
