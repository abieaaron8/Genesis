# Genesis Pipeline Test Report

## Scope

This report covers the ML-aware verification pipeline, the existing FastAPI endpoints, evidence ranking, and error handling. Tests were run against the local backend from `backend/` with the trained model at `backend/models/genesis_distilbert/`.

## Results

| Test | Result | Evidence |
|---|---|---|
| Backend OpenAPI availability | PASS | `GET /openapi.json` returned HTTP 200 |
| DistilBERT prediction endpoint | PASS | `POST /api/model/predict` returned prediction, label, confidence, probabilities, and device |
| GPU selection | PASS | Prediction response reported `device: cuda` |
| Probability validity | PASS | REAL and FAKE probabilities were bounded and summed to approximately 1.0 |
| Invalid model input | PASS | A one-character claim returned HTTP 422 with validation details |
| ML context propagation | PASS | Graph state retained `model_prediction` and retrieval metadata retained the prediction context |
| Dual query generation | PASS | Retrieval metadata contained the original claim and the ML classification-context query |
| Hybrid evidence ranking | PASS | Ranked records contained semantic, credibility, recency, hybrid, and final scores |
| Recency scoring | PASS | Recent evidence received a higher recency score than equivalent older evidence |
| Graph verdict synthesis | PASS | The graph returned verdict, confidence, judge output, evidence, and completed stages with mocked evidence |
| Existing `/api/verify` | PASS | Returned HTTP 200 with verdict, confidence, reasoning, evidence summary, and model prediction |
| Evidence summary | PASS | Response contained supporting/contradicting counts and top-source information |

## Live endpoint sample

`POST /api/model/predict` returned:

- Prediction: `REAL`
- Confidence: `0.923876`
- Device: `cuda`
- Probabilities: `REAL=0.923876`, `FAKE=0.076124`

`POST /api/verify` returned a source-backed `FALSE` verdict for the microchip claim with confidence, reasoning points, prosecutor/defender arguments, retrieval metadata, and `evidence_summary`.

## Issues fixed or handled

- Corrected the end-to-end test execution context: backend modules use top-level imports and must be run from `backend/`.
- Adjusted verification to test the actual graph state contract rather than assuming a narrower result shape.
- Confirmed provider failures do not prevent deterministic evidence-backed fallback behavior.

## Remaining non-blocking warnings

- The configured Groq and Gemini credentials reported authentication failures during one graph test.
- Ollama was reachable but did not have the configured `mistral:latest` model.
- These provider warnings were handled by the existing fallback logic; the live `/api/verify` request still completed successfully using available curated/fallback evidence.
- Existing duplicate FastAPI operation-id warnings remain unrelated to the ML-aware pipeline.

## Conclusion

The ML-aware verification pipeline is operational. DistilBERT influences retrieval context, evidence ranking includes semantic similarity, credibility, and recency, downstream stages return structured reasoning, and existing verification APIs remain functional.
