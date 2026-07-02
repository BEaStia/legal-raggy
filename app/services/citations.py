"""Citation service: attach legal citations to compliance assessments.

Maps regulatory triggers to retrieval queries, searches the local corpus,
and produces LegalCitation objects with provenance.
"""

from pathlib import Path

from app.models import ComplianceAssessment, LegalCitation, RegulatoryTrigger
from app.retrieval.keyword import KeywordRetriever

_TRIGGER_QUERIES: dict[str, str] = {
    "personal_data_processing": "персональные данные обработка",
    "possible_ispdn": "информационная система персональных данных ИСПДн",
    "privacy_policy_required": "политика обработки персональных данных",
    "security_measures_required": "требования к защите персональных данных",
    "electronic_signature_regulation": "электронная подпись ЭП УКЭП",
    "commercial_secret_possible": "коммерческая тайна конфиденциальность",
    "payment_regulation_possible": "платёжные операции перевод National Payment System",
    "kii_relevance_possible": "критическая информационная инфраструктура КИИ",
    "possible_cross_border_transfer": "трансграничная передача персональных данных",
    "external_processor_or_transfer_unknown": "передача данных обработчик третьим лицам",
}


def _trigger_to_query(trigger: RegulatoryTrigger) -> str | None:
    """Get retrieval query for a trigger ID. Returns None if no mapping exists."""
    return _TRIGGER_QUERIES.get(trigger.id)


def _chunk_to_citation(
    chunk_text: str,
    chunk_id: str,
    document_title: str,
    document_type: str | None,
    source_path: str,
) -> LegalCitation:
    """Convert a retrieved chunk into a LegalCitation.

    Extracts article/part from heading if present, uses first ~200 chars as quote.
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


def attach_citations(
    assessment: ComplianceAssessment,
    laws_dir: Path | None = None,
    top_k: int = 2,
) -> ComplianceAssessment:
    """Attach legal citations to an assessment based on its triggers.

    For each regulatory trigger, searches the corpus with a predefined query
    and attaches the top results as LegalCitation objects.

    Args:
        assessment: ComplianceAssessment with regulatory_triggers populated.
        laws_dir: Path to the laws corpus directory. If None or non-existent,
                  returns assessment unchanged (no citations).
        top_k: Maximum citations per trigger.

    Returns:
        Assessment with citations list populated.
    """
    if not assessment.regulatory_triggers:
        return assessment

    if laws_dir is None or not laws_dir.is_dir():
        return assessment

    try:
        retriever = KeywordRetriever(corpus_dirs=[laws_dir])
    except Exception:
        return assessment

    if not retriever.chunks:
        return assessment

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
