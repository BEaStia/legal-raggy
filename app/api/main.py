from fastapi import FastAPI

from app.api.routes import analyze, health

app = FastAPI(title="legal-raggy", version="0.1.0")
app.include_router(health.router)
app.include_router(analyze.router)
