# Матрица трассировки Milestone 1

| Requirement | Source | Task | Verification | ADR | Review | Article |
|---|---|---|---|---|---|---|
| FastAPI, health, Docker | Brief 5, 10.1, 16.1 | TASK-0001 | `tests/test_health.py` + smoke | ADR-0002 | REVIEW-0001 | `.articles/0001-project-skeleton.md` |
| Core models | Brief 7, 16.2 | TASK-0002 | `tests/test_models.py` | ADR-0002 | REVIEW-0002 | `.articles/0002-core-models.md` |
| Heuristic extraction | Brief 9, 15.2, 16.3 | TASK-0003 | `tests/test_extractor.py` | ADR-0002 | REVIEW-0003 | `.articles/0003-heuristic-extractor.md` |
| Deterministic rules | Brief 8, 15.3, 16.4 | TASK-0004 | `tests/test_rule_engine.py` | ADR-0002 | REVIEW-0004 | `.articles/0004-rule-engine.md` |
| Analyze API | Brief 10.2, 16.5 | TASK-0005 | `tests/test_analyze_api.py` | ADR-0002 | REVIEW-0005 | `.articles/0005-analyze-endpoint.md` |
| Markdown report | Brief 14, 15.4, 16.6 | TASK-0006 | `tests/test_renderer.py` | ADR-0002 | REVIEW-0006 | `.articles/0006-markdown-renderer.md` |
| Local retrieval | Brief 11–13, 16.7 | TASK-0007 | `tests/test_retrieval.py` | ADR-0002 | REVIEW-0007 | `.articles/0007-local-corpus-loader.md` |
| Grounded citations | Brief 16.8 | TASK-0008 | `tests/test_citations.py` | ADR-0002 | REVIEW-0008 | `.articles/0008-assessment-citations.md` |

# Матрица трассировки Milestone 2

| Requirement | Source | Task | Verification | ADR | Review | Article |
|---|---|---|---|---|---|---|
| Qdrant + dense retrieval | Brief 19 | TASK-0009 | `tests/test_dense_retrieval.py` | ADR-0002 | REVIEW-0004 | `.articles/0009-qdrant-embeddings.md` |
| Hybrid retrieval | Milestone 2 plan | TASK-0010 | `tests/test_hybrid_retrieval.py` | ADR-0002 | REVIEW-0004 | `.articles/0010-hybrid-retrieval.md` |
| Hybrid citations | Milestone 2 plan | TASK-0011, TASK-0019 | `tests/test_hybrid_citations.py`, `tests/test_hybrid_citations_production.py` | ADR-0002 | REVIEW-0004 | `.articles/0011-hybrid-citations.md`, `.articles/0019-hybrid-citations.md` |
| Evaluation framework | Milestone 2 plan | TASK-0016 | `app.evaluation.metrics.run_evaluation()` | ADR-0002 | REVIEW-0004 | `.articles/0016-evaluation.md` |
| Real corpus and freshness | Milestone 2 plan | TASK-0017, TASK-0018 | `tests/test_laws_update_cron.py`, `docker build --target laws-updater`, container `--check` | ADR-0002 | REVIEW-0004 | `.articles/0017-real-laws-fetcher.md`, `.articles/0018-auto-update-laws.md` |
| Search API | TASK-0019 handoff | TASK-0020 | `tests/test_search_api.py` | ADR-0002 | REVIEW-0005 | `.articles/0020-search-endpoint.md` |

# Матрица трассировки Milestone 3+

| Requirement | Source | Task | Verification | ADR | Review | Article |
|---|---|---|---|---|---|---|
| LLM extraction evaluation | Milestone 3 quality hardening | TASK-0021 | `tests/test_evaluation.py`, `tests/test_llm_extractor.py` | ADR-0002 | REVIEW-0006 | `.articles/0021-llm-extraction-eval.md` |
