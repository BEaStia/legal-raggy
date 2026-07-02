from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    chunk_id: str
    document_title: str
    document_type: str | None = None
    source_path: str
    heading: str | None = None
    text: str
    metadata: dict = Field(default_factory=dict)


class RetrievedChunk(BaseModel):
    chunk: DocumentChunk
    score: float
    match_reason: str | None = None
