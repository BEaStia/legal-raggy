"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from qdrant_client import QdrantClient

from app.api.middleware import RateLimitMiddleware, RequestIDMiddleware
from app.api.routes import admin, analyze, health, search
from app.core.config import LAWS_DIR, settings
from app.core.logging import setup_logging
from app.ingestion.chunking import load_corpus
from app.retrieval.dense import DenseRetriever
from app.retrieval.keyword import KeywordRetriever
from app.retrieval.qdrant_store import create_collection, index_chunks

setup_logging()


class AppState:
    """Shared application state."""

    keyword_retriever: KeywordRetriever | None = None
    dense_retriever: DenseRetriever | None = None
    qdrant_client: QdrantClient | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize shared resources on startup, clean up on shutdown."""
    state = app.state

    # Initialize keyword retriever
    if LAWS_DIR.exists():
        chunks = load_corpus(LAWS_DIR)
        state.keyword_retriever = KeywordRetriever()
        state.keyword_retriever.load_chunks(chunks)

    # Initialize Qdrant connection
    try:
        client = QdrantClient(url=settings.qdrant_url, timeout=5)
        client.get_collections()
        state.qdrant_client = client

        if LAWS_DIR.exists():
            chunks = load_corpus(LAWS_DIR)
            if chunks:
                create_collection(client, settings.QDRANT_COLLECTION)
                index_chunks(client, chunks, settings.QDRANT_COLLECTION)
                state.dense_retriever = DenseRetriever(client, settings.QDRANT_COLLECTION)
    except Exception:
        pass

    yield

    # Cleanup
    if state.qdrant_client:
        state.qdrant_client.close()


app = FastAPI(title="legal-raggy", version="0.1.0", lifespan=lifespan)

app.add_middleware(RequestIDMiddleware)
app.add_middleware(RateLimitMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_V1_PREFIX = "/api/v1"

app.include_router(health.router, prefix=API_V1_PREFIX)
app.include_router(analyze.router, prefix=API_V1_PREFIX)
app.include_router(search.router, prefix=API_V1_PREFIX)
app.include_router(admin.router, prefix=API_V1_PREFIX)
