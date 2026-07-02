"""Tests for local corpus loader and keyword retriever."""

from pathlib import Path

import pytest

from app.ingestion.chunking import chunk_by_headings, load_corpus
from app.ingestion.loaders import discover_markdown_files, load_markdown_file, parse_frontmatter
from app.models.retrieval import DocumentChunk
from app.retrieval.keyword import KeywordRetriever


class TestParseFrontmatter:
    def test_parses_yaml_frontmatter(self):
        text = """---
document_title: "Test Law"
document_type: "federal_law"
---

# Heading

Body text here.
"""
        metadata, body = parse_frontmatter(text)
        assert metadata["document_title"] == "Test Law"
        assert metadata["document_type"] == "federal_law"
        assert body.startswith("# Heading")

    def test_returns_empty_dict_when_no_frontmatter(self):
        text = "# No frontmatter\n\nJust body."
        metadata, body = parse_frontmatter(text)
        assert metadata == {}
        assert body == "# No frontmatter\n\nJust body."

    def test_handles_invalid_yaml_gracefully(self):
        text = """---
invalid: yaml: [
---

Body.
"""
        metadata, body = parse_frontmatter(text)
        assert metadata == {}
        assert "Body." in body


class TestLoadMarkdownFile:
    def test_loads_file_with_frontmatter(self, tmp_path: Path):
        md = tmp_path / "test.md"
        md.write_text('---\ndocument_title: "Test"\n---\n\n# Heading\n\nBody.', encoding="utf-8")
        metadata, body = load_markdown_file(md)
        assert metadata["document_title"] == "Test"
        assert "Body." in body

    def test_raises_for_non_md_file(self, tmp_path: Path):
        txt = tmp_path / "test.txt"
        txt.write_text("hello", encoding="utf-8")
        with pytest.raises(ValueError, match="Expected .md file"):
            load_markdown_file(txt)


class TestDiscoverMarkdownFiles:
    def test_finds_md_files_recursively(self, tmp_path: Path):
        (tmp_path / "a.md").write_text("# A", encoding="utf-8")
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "b.md").write_text("# B", encoding="utf-8")
        (sub / "c.txt").write_text("C", encoding="utf-8")

        files = discover_markdown_files(tmp_path)
        assert len(files) == 2
        assert all(f.suffix == ".md" for f in files)

    def test_returns_empty_for_nonexistent_dir(self):
        assert discover_markdown_files(Path("/nonexistent/path")) == []


class TestChunkByHeadings:
    def test_splits_by_headings(self, tmp_path: Path):
        md = tmp_path / "law.md"
        md.write_text(
            '---\ndocument_title: "Test Law"\n---\n\n'
            "# Section One\n\nContent one.\n\n"
            "# Section Two\n\nContent two.",
            encoding="utf-8",
        )
        chunks = chunk_by_headings(md)
        assert len(chunks) == 2
        assert chunks[0].heading == "Section One"
        assert "Content one." in chunks[0].text
        assert chunks[1].heading == "Section Two"
        assert "Content two." in chunks[1].text

    def test_includes_provenance(self, tmp_path: Path):
        md = tmp_path / "law.md"
        md.write_text(
            '---\ndocument_title: "Test Law"\n'
            'document_type: "federal_law"\n---\n\n'
            "# Intro\n\nText.",
            encoding="utf-8",
        )
        chunks = chunk_by_headings(md)
        assert chunks[0].document_title == "Test Law"
        assert chunks[0].document_type == "federal_law"
        assert str(md) in chunks[0].source_path
        assert "document_type" in chunks[0].metadata

    def test_single_chunk_when_no_headings(self, tmp_path: Path):
        md = tmp_path / "plain.md"
        md.write_text("Just plain text without headings.", encoding="utf-8")
        chunks = chunk_by_headings(md)
        assert len(chunks) == 1
        assert chunks[0].heading is None

    def test_stable_chunk_ids(self, tmp_path: Path):
        md = tmp_path / "law.md"
        md.write_text("# Section A\n\nText A.\n\n# Section B\n\nText B.", encoding="utf-8")
        chunks1 = chunk_by_headings(md)
        chunks2 = chunk_by_headings(md)
        assert [c.chunk_id for c in chunks1] == [c.chunk_id for c in chunks2]


class TestLoadCorpus:
    def test_loads_all_files_from_directory(self, tmp_path: Path):
        (tmp_path / "a.md").write_text("# A\n\nText A.", encoding="utf-8")
        (tmp_path / "b.md").write_text("# B\n\nText B.", encoding="utf-8")
        chunks = load_corpus(tmp_path)
        assert len(chunks) == 2

    def test_returns_empty_for_empty_directory(self, tmp_path: Path):
        assert load_corpus(tmp_path) == []


class TestKeywordRetriever:
    @pytest.fixture
    def retriever(self) -> KeywordRetriever:
        chunks = [
            DocumentChunk(
                chunk_id="chunk1",
                document_title="152-ФЗ",
                document_type="federal_law",
                source_path="laws/152fz.md",
                heading="Персональные данные",
                text=(
                    "Персональные данные — любая информация, относящаяся "
                    "к прямо или косвенно определённому физическому лицу. "
                    "Обработка персональных данных требует согласия субъекта."
                ),
                metadata={"domain": "personal_data"},
            ),
            DocumentChunk(
                chunk_id="chunk2",
                document_title="63-ФЗ",
                document_type="federal_law",
                source_path="laws/63fz.md",
                heading="Электронная подпись",
                text=(
                    "Электронная подпись — информация в электронной форме, "
                    "присоединённая к другой информации. "
                    "Усиленная квалифицированная электронная подпись "
                    "признаётся равнозначной собственноручной."
                ),
                metadata={"domain": "electronic_signature"},
            ),
            DocumentChunk(
                chunk_id="chunk3",
                document_title="98-ФЗ",
                document_type="federal_law",
                source_path="laws/98fz.md",
                heading="Коммерческая тайна",
                text=(
                    "Коммерческая тайна — режим конфиденциальности информации. "
                    "Обладатель информации должен принять меры "
                    "по охране конфиденциальности."
                ),
                metadata={"domain": "commercial_secret"},
            ),
        ]
        r = KeywordRetriever()
        r.load_chunks(chunks)
        return r

    def test_finds_relevant_chunk_for_personal_data(self, retriever: KeywordRetriever):
        results = retriever.search("персональные данные обработка согласие", top_k=3)
        assert len(results) >= 1
        assert results[0].chunk.document_title == "152-ФЗ"
        assert results[0].score > 0

    def test_finds_relevant_chunk_for_electronic_signature(self, retriever: KeywordRetriever):
        results = retriever.search("электронная подпись квалифицированная", top_k=3)
        assert len(results) >= 1
        assert results[0].chunk.document_title == "63-ФЗ"

    def test_returns_empty_for_no_match(self, retriever: KeywordRetriever):
        results = retriever.search("xyznonexistent", top_k=5)
        assert results == []

    def test_respects_top_k(self, retriever: KeywordRetriever):
        results = retriever.search("данные информация", top_k=1)
        assert len(results) == 1

    def test_results_have_scores_and_reasons(self, retriever: KeywordRetriever):
        results = retriever.search("персональные данные", top_k=3)
        for r in results:
            assert r.score > 0
            assert r.match_reason is not None

    def test_scores_ordered_descending(self, retriever: KeywordRetriever):
        results = retriever.search("данные информация подпись", top_k=5)
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_heading_boost(self, retriever: KeywordRetriever):
        results = retriever.search("персональные данные", top_k=3)
        pd_chunk = next(r for r in results if r.chunk.document_title == "152-ФЗ")
        ct_chunk = next((r for r in results if r.chunk.document_title == "98-ФЗ"), None)
        assert pd_chunk.score >= (ct_chunk.score if ct_chunk else 0)

    def test_loads_from_real_corpus(self):
        project_root = Path(__file__).parent.parent
        laws_dir = project_root / "data" / "raw" / "laws"
        if laws_dir.is_dir():
            retriever = KeywordRetriever(corpus_dirs=[laws_dir])
            assert len(retriever.chunks) > 0
            results = retriever.search("персональные данные обработка", top_k=5)
            assert len(results) > 0
            assert any("152" in r.chunk.document_title for r in results)

    def test_deterministic_ordering(self, retriever: KeywordRetriever):
        q = "персональные данные обработка"
        r1 = retriever.search(q, top_k=5)
        r2 = retriever.search(q, top_k=5)
        assert [r.chunk.chunk_id for r in r1] == [r.chunk.chunk_id for r in r2]
