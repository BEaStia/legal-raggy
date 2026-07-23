FROM python:3.12-slim AS base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DEFAULT_TIMEOUT=300 \
    PIP_RETRIES=10

COPY pyproject.toml README.md ./

FROM base AS api

COPY app ./app
COPY scripts ./scripts

RUN pip install .

EXPOSE 8000

CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM base AS laws-updater

COPY scripts ./scripts

RUN pip install beautifulsoup4 httpx pyyaml

CMD ["python", "scripts/update_laws_cron.py"]
