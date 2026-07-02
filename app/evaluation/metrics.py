"""Evaluation metrics for compliance assessment."""

from dataclasses import dataclass

from app.evaluation.datasets import GOLDEN_DATASET, GoldenCase
from app.rules.architecture_patterns import extract_architecture_profile
from app.rules.engine import analyze_profile


@dataclass
class EvalResult:
    """Result of evaluating a single golden case."""

    case_id: str
    trigger_precision: float
    trigger_recall: float
    category_precision: float
    category_recall: float
    citation_coverage: float
    false_positives: list[str]
    false_negatives: list[str]


def _precision_recall(predicted: set[str], expected: set[str]) -> tuple[float, float]:
    """Compute precision and recall."""
    if not expected and not predicted:
        return 1.0, 1.0
    if not expected:
        return 0.0, 1.0
    if not predicted:
        return 0.0, 0.0
    tp = len(predicted & expected)
    precision = tp / len(predicted)
    recall = tp / len(expected)
    return precision, recall


def evaluate_case(case: GoldenCase) -> EvalResult:
    """Evaluate a single golden case."""
    profile = extract_architecture_profile(case.description)
    assessment = analyze_profile(profile)

    predicted_triggers = {t.id for t in assessment.regulatory_triggers}
    expected_triggers = set(case.expected_triggers)

    predicted_categories = {c.value for c in profile.data_categories}
    expected_categories = set(case.expected_data_categories)

    trigger_precision, trigger_recall = _precision_recall(
        predicted_triggers, expected_triggers
    )
    category_precision, category_recall = _precision_recall(
        predicted_categories, expected_categories
    )

    # Citation coverage: fraction of triggers that have at least one citation
    # (simplified: check if any citations exist when triggers exist)
    has_triggers = len(expected_triggers) > 0
    has_citations = len(assessment.citations) > 0
    citation_coverage = 1.0 if (has_triggers and has_citations) or not has_triggers else 0.0

    false_positives = list(predicted_triggers - expected_triggers)
    false_negatives = list(expected_triggers - predicted_triggers)

    return EvalResult(
        case_id=case.id,
        trigger_precision=trigger_precision,
        trigger_recall=trigger_recall,
        category_precision=category_precision,
        category_recall=category_recall,
        citation_coverage=citation_coverage,
        false_positives=false_positives,
        false_negatives=false_negatives,
    )


def run_evaluation() -> dict:
    """Run evaluation over the full golden dataset."""
    results = [evaluate_case(case) for case in GOLDEN_DATASET]

    avg_trigger_precision = sum(r.trigger_precision for r in results) / len(results)
    avg_trigger_recall = sum(r.trigger_recall for r in results) / len(results)
    avg_category_precision = sum(r.category_precision for r in results) / len(results)
    avg_category_recall = sum(r.category_recall for r in results) / len(results)
    avg_citation_coverage = sum(r.citation_coverage for r in results) / len(results)

    total_fp = sum(len(r.false_positives) for r in results)
    total_fn = sum(len(r.false_negatives) for r in results)

    return {
        "n_cases": len(results),
        "avg_trigger_precision": round(avg_trigger_precision, 3),
        "avg_trigger_recall": round(avg_trigger_recall, 3),
        "avg_category_precision": round(avg_category_precision, 3),
        "avg_category_recall": round(avg_category_recall, 3),
        "avg_citation_coverage": round(avg_citation_coverage, 3),
        "total_false_positives": total_fp,
        "total_false_negatives": total_fn,
        "results": results,
    }
