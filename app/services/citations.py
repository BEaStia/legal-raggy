"""Citation service: attach legal citations to compliance assessments.

Maps regulatory triggers to retrieval queries, searches the local corpus
using hybrid retrieval (keyword + dense), and produces LegalCitation
objects with provenance. Falls back to keyword-only if Qdrant is unavailable.
"""

import logging
from pathlib import Path

from qdrant_client import QdrantClient

from app.core.config import settings
from app.models import ComplianceAssessment, LegalCitation, RegulatoryTrigger
from app.retrieval.dense import DenseRetriever
from app.retrieval.hybrid import HybridRetriever
from app.retrieval.keyword import KeywordRetriever
from app.retrieval.qdrant_store import (
    create_collection,
    index_chunks,
)

logger = logging.getLogger(__name__)

_TRIGGER_QUERIES: dict[str, str] = {
    "personal_data_processing": "персональные данные обработка",
    "possible_ispdn": "информационная система персональных данных ИСПДн",
    "privacy_policy_required": "политика обработки персональных данных",
    "security_measures_required": "требования к защите персональных данных",
    "electronic_signature_regulation": "электронная подпись ЭП УКЭП",
    "commercial_secret_possible": "коммерческая тайна конфиденциальность",
    "payment_regulation_possible": (
        "платёжные операции перевод National Payment System"
    ),
    "kii_relevance_possible": "критическая информационная инфраструктура КИИ",
    "possible_cross_border_transfer": (
        "трансграничная передача персональных данных"
    ),
    "external_processor_or_transfer_unknown": (
        "передача данных обработчик третьим лицам"
    ),
}


def _trigger_to_query(trigger: RegulatoryTrigger) -> str | None:
    """Get retrieval query for a trigger ID. Returns None if no mapping."""
    return _TRIGGER_QUERIES.get(trigger.id)


def _chunk_to_citation(
    chunk_text: str,
    chunk_id: str,
    document_title: str,
    document_type: str | None,
    source_path: str,
) -> LegalCitation:
    """Convert a retrieved chunk into a LegalCitation.

    Extracts article/part from heading if present, uses first 300 chars
    as quote.
    """
    heading: str | None = None

    lines = chunk_text.split("\n")
    if lines and lines[0].startswith("#"):
        heading = lines[0].lstrip("# ").strip()

    quote = chunk_text[:300].strip()
    if len(chunk_text) > 300:
        quote += "..."

    return LegalCitation(
        document_title=document_title,
        document_type=document_type,
        article=heading,
        quote=quote,
        source=source_path,
        chunk_id=chunk_id,
    )


def _try_create_qdrant_client() -> QdrantClient | None:
    """Try to connect to Qdrant, return None if unavailable."""
    try:
        client = QdrantClient(
            url=settings.qdrant_url,
            timeout=5,
        )
        client.get_collections()
        return client
    except Exception:
        return None


def attach_citation(
    assessment: ComplianceAssessment,
    laws_dir: Path | None = None,
    top_k: int = 2,
    use_hybrid: bool = True,
) -> ComplianceAssessment:
    """Attach legal citations to an assessment based on its triggers.

    Uses hybrid retrieval (keyword + dense) by default. Falls back to
    keyword-only if Qdrant is unavailable.

    Args:
        assessment: ComplianceAssessment with regulatory_triggers populated.
        laws_dir: Path to the laws corpus directory. If None or non-existent,
                  returns assessment unchanged (no citations).
        top_k: Maximum citations per trigger.
        use_hybrid: Use hybrid retrieval (default True). Falls back to
                    keyword if Qdrant is unavailable.

    Returns:
        Assessment with citations list populated.
    """
    if not assessment.regulatory_triggers:
        return assessment

    if laws_dir is None or not laws_dir.is_dir():
        return assessment

    keyword_retriever = KeywordRetriever(corpus_dirs=[laws_dir])
    if not keyword_retriever.chunks:
        return assessment

    if use_hybrid:
        qdrant_client = _try_create_qdrant_client()
        if qdrant_client is not None:
            return _attach_with_hybrid(
                assessment,
                keyword_retriever,
                qdrant_client,
                laws_dir,
                top_k,
            )
        logger.info("Qdrant unavailable, falling back to keyword retrieval")

    return _attach_with_keyword(assessment, keyword_retriever, top_k)


def _attach_with_hybrid(
    assessment: ComplianceAssessment,
    keyword_retriever: KeywordRetriever,
    qdrant_client: QdrantClient,
    laws_dir: Path,
    top_k: int,
) -> ComplianceAssessment:
    """Attach citations using hybrid retrieval."""
    from app.ingestion.chunking import load_corpus

    try:
        chunks = load_corpus(laws_dir)
        create_collection(qdrant_client, settings.QDRANT_COLLECTION)
        index_chunks(qdrant_client, chunks, settings.QDRANT_COLLECTION)
    except Exception as e:
        logger.warning("Failed to index corpus in Qdrant: %s", e)
        return _attach_with_keyword(assessment, keyword_retriever, top_k)

    dense_retriever = DenseRetriever(
        qdrant_client, settings.QDRANT_COLLECTION
    )
    hybrid = HybridRetriever(keyword_retriever, dense_retriever)

    return _attach_with_retriever(assessment, hybrid, top_k)


def _attach_with_keyword(
    assessment: ComplianceAssessment,
    keyword_retriever: KeywordRetriever,
    top_k: int,
) -> ComplianceAssessment:
    """Attach citations using keyword-only retrieval."""
    return _attach_with_retriever(assessment, keyword_retriever, top_k)


def _attach_with_retriever(
    assessment: ComplianceAssessment,
    retriever,
    top_k: int,
) -> ComplianceAssessment:
    """Attach citations using any retriever with search(query, top_k)."""
    citations: list[LegalCitation] = []
    seen_chunk_ids: set[str] = set()

    for trigger in assessment.regulatory_triggers:
        query = _trigger_to_query(trigger)
        if not query:
            continue

        results = retriever.search(query, top_k=top_k)
        for result in results:
            if result.chunk.chunk_id in seen_chunk_ids:
                continue
            seen_chunk_ids.add(result.chunk.chunk_id)

            citation = _chunk_to_citation(
                chunk_text=result.chunk.text,
                chunk_id=result.chunk.chunk_id,
                document_title=result.chunk.document_title,
                document_type=result.chunk.document_type,
                source_path=result.chunk.source_path,
            )
            citations.append(citation)

    assessment.citations = citations
    return assessment
