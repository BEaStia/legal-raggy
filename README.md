# legal-raggy

Preliminary IT architecture compliance review under Russian regulation. The system analyzes architecture descriptions, applies deterministic rules, and returns structured assessments with citations.

This milestone starts with a minimal API skeleton — no external API keys required.

## Requirements

- Python 3.12+
- Docker and Docker Compose (optional, for containerized runs)

## Local development

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn app.api.main:app --reload --port 8000
```

Check health:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status": "ok"}
```

## Docker

```bash
docker compose up --build
```

Then open `http://localhost:8000/health`.

## Tests

```bash
pytest tests/test_health.py -v
```

## Documentation

Project workflow, decisions, and tasks live in the repository root (`.tasks/`, `.decisions/`, `.handoff/`). See [AGENTS.md](AGENTS.md) for contributor rules.

Legal assessments produced by this system are preliminary and require human legal review.
