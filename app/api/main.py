from fastapi import FastAPI

from app.api.routes import admin, analyze, health, search

app = FastAPI(title="legal-raggy", version="0.1.0")
app.include_router(health.router)
app.include_router(analyze.router)
app.include_router(search.router)
app.include_router(admin.router)
