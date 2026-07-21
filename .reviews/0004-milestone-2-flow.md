---
id: REVIEW-0004
task: MILESTONE-2
reviewed_commit: f5f29b1
reviewer: codex
status: passed-with-follow-up
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

### Finding 3: Corpus freshness is improved but not release-closed
`TASK-0018` added structured `changed/skipped/failed` update results, weekly cron
configuration, JSON update logs, and a task article. The task is correctly kept
in `.tasks/in-progress` because container smoke verification did not complete.
The Dockerfile now copies `scripts/`, which is required by the `laws-updater`
compose command, but the Docker build was interrupted during heavy ML dependency
installation and should not be reported as passed.

Verdict: follow-up required before release closure.

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

Milestone 2 should not be marked release-complete until `TASK-0018` finishes its
container smoke-check and moves from `in-progress` to `ready-for-release`.

Recommended next action:
1. Finish `TASK-0018` container smoke-check for `laws-updater`.
2. Move `TASK-0018` to `ready-for-release` if the smoke-check passes.
3. Then create the next explicit task for the next milestone rather than relying
   on the stale handoff wording.
