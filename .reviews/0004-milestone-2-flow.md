---
id: REVIEW-0004
task: MILESTONE-2
reviewed_commit: f5f29b1
reviewer: codex
status: passed
created_at: 2026-07-21
---

# Milestone 2 Flow Review

## Scope
Milestone 2 covers the retrieval and grounding flow around the legal corpus:

- dense retrieval infrastructure (`TASK-0009`);
- hybrid keyword + dense retrieval (`TASK-0010`);
- hybrid citations in assessment and production pipelines (`TASK-0011`, `TASK-0019`);
- evaluation dataset and metrics (`TASK-0016`);
- real-law corpus ingestion and freshness automation (`TASK-0017`, `TASK-0018`).

The review focuses on whether the system has a coherent end-to-end flow from
architecture description to grounded citations, and whether it is ready to be
treated as release-complete.

## Automated evidence
- `python -m pytest tests/test_laws_update_cron.py -q` — passed on 2026-07-20.
- `ruff check app scripts/fetch_laws.py scripts/update_laws_cron.py tests/test_laws_update_cron.py` — passed on 2026-07-20.
- `mypy app` — passed on 2026-07-20.
- `python scripts/check_docs.py --all` — passed on 2026-07-20.
- `python -m pre_commit run --all-files` — passed on 2026-07-21.
- `docker build --target laws-updater -t legal-raggy-laws-updater:task-0018 .` — passed on 2026-07-21.
- `docker run --rm legal-raggy-laws-updater:task-0018 python scripts/update_laws_cron.py --check` — passed on 2026-07-21.
- `docker compose build laws-updater` — passed on 2026-07-21.
- Full `python -m pytest -q` — passed with network access on 2026-07-20: `196 passed`.
- Independent review of TASK-0018 changes found no discrete correctness issues.

## Flow Findings

### Finding 1: Retrieval flow is coherent
`run_analysis()` extracts an architecture profile, runs deterministic compliance
analysis, and attaches citations from the configured laws directory.
`attach_citation()` uses hybrid retrieval by default and falls back to keyword
retrieval when Qdrant is unavailable. The search API exposes keyword, dense and
hybrid modes with the same fallback behavior for hybrid search.

Verdict: pass.

### Finding 2: Grounding has explicit workflow routing
The LangGraph workflow performs extract -> detect -> retrieve -> grounding check
-> warning/finalize. Missing citations do not silently pass as grounded output;
the workflow can route through a warning node before finalization.

Verdict: pass.

### Finding 3: Corpus freshness is release-closed
`TASK-0018` added structured `changed/skipped/failed` update results, weekly cron
configuration, JSON update logs, `--check` smoke mode, and a task article. The
Dockerfile now has a lightweight `laws-updater` target, so the cron smoke-check
does not depend on full API ML dependencies. The target build, container
`--check` run, and compose build now pass.

Verdict: pass.

### Finding 4: Verification boundary is understood
Dense and hybrid tests depend on the HuggingFace embedding model. In the current
environment, full pytest can fail in the sandbox due to DNS/network restrictions
and pass when rerun with network access. This is an environment constraint, not
evidence of retrieval logic failure.

Verdict: pass with documented caveat.

## Verdict
Milestone 2 is functionally coherent for local RAG flow: corpus loading,
keyword/dense/hybrid retrieval, citation attachment, fallback behavior,
workflow grounding, and evaluation are connected.

Milestone 2 can be treated as release-complete for the local RAG flow and corpus
freshness automation.

Recommended next action:
1. Create the next explicit task for Milestone 3.
2. Keep external notification delivery for law update events as a separate
   follow-up if it becomes necessary.
