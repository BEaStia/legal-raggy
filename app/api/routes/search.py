"""Search API routes."""

from typing import Literal

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from app.core.config import LAWS_DIR, settings
from app.ingestion.chunking import load_corpus
from app.retrieval.dense import DenseRetriever
from app.retrieval.hybrid import HybridRetriever
from app.retrieval.keyword import KeywordRetriever
from app.retrieval.qdrant_store import create_collection, index_chunks

router = APIRouter()


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=3, description="Search query text")
    top_k: int = Field(5, ge=1, le=20, description="Number of results")
    mode: Literal["keyword", "dense", "hybrid"] = Field("hybrid", description="Retrieval mode")


class SearchResult(BaseModel):
    chunk_id: str
    document_title: str
    heading: str | None
    text: str
    score: float
    source_path: str


class SearchResponse(BaseModel):
    query: str
    mode: str
    total_results: int
    results: list[SearchResult]


def _get_keyword_retriever(state) -> KeywordRetriever:
    """Get keyword retriever from app state or create on demand."""
    if hasattr(state, "keyword_retriever") and state.keyword_retriever is not None:
        return state.keyword_retriever

    retriever = KeywordRetriever()
    if LAWS_DIR.exists():
        chunks = load_corpus(LAWS_DIR)
        retriever.load_chunks(chunks)
    return retriever


def _get_dense_retriever(state) -> DenseRetriever | None:
    """Get dense retriever from app state or create on demand."""
    if hasattr(state, "dense_retriever") and state.dense_retriever is not None:
        return state.dense_retriever

    from qdrant_client import QdrantClient

    try:
        client = QdrantClient(url=settings.qdrant_url, timeout=5)
        client.get_collections()

        if LAWS_DIR.exists():
            chunks = load_corpus(LAWS_DIR)
            if chunks:
                create_collection(client, settings.QDRANT_COLLECTION)
                index_chunks(client, chunks, settings.QDRANT_COLLECTION)
                return DenseRetriever(client, settings.QDRANT_COLLECTION)
    except Exception:
        pass
    return None


@router.post("/search", response_model=SearchResponse)
async def search_corpus(request: Request, body: SearchRequest):
    """Search the legal corpus using keyword, dense, or hybrid retrieval."""
    state = request.app.state
    results = []

    if body.mode == "keyword":
        retriever = _get_keyword_retriever(state)
        results = retriever.search(body.query, top_k=body.top_k)

    elif body.mode == "dense":
        dense_retriever = _get_dense_retriever(state)
        if dense_retriever is None:
            raise HTTPException(
                status_code=503,
                detail="Dense retrieval unavailable: Qdrant not connected",
            )
        results = dense_retriever.search(body.query, top_k=body.top_k)

    elif body.mode == "hybrid":
        kw_retriever = _get_keyword_retriever(state)
        dense_retriever = _get_dense_retriever(state)

        if dense_retriever is None:
            # Fallback to keyword if Qdrant unavailable
            results = kw_retriever.search(body.query, top_k=body.top_k)
        else:
            hybrid = HybridRetriever(kw_retriever, dense_retriever)
            results = hybrid.search(body.query, top_k=body.top_k)

    else:
        raise HTTPException(status_code=400, detail=f"Unknown mode: {body.mode}")

    return SearchResponse(
        query=body.query,
        mode=body.mode,
        total_results=len(results),
        results=[
            SearchResult(
                chunk_id=r.chunk.chunk_id,
                document_title=r.chunk.document_title,
                heading=r.chunk.heading,
                text=r.chunk.text[:500] + ("..." if len(r.chunk.text) > 500 else ""),
                score=r.score,
                source_path=r.chunk.source_path,
            )
            for r in results
        ],
    )
