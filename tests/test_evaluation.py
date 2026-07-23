"""Tests for evaluation framework."""

import json

from app.evaluation.datasets import GOLDEN_DATASET
from app.evaluation.metrics import (
    EvalResult,
    _precision_recall,
    evaluate_case,
    run_evaluation,
)


class TestPrecisionRecall:
    def test_perfect_match(self) -> None:
        p, r = _precision_recall({"a", "b"}, {"a", "b"})
        assert p == 1.0
        assert r == 1.0

    def test_partial_match(self) -> None:
        p, r = _precision_recall({"a", "b"}, {"a", "c"})
        assert p == 0.5
        assert r == 0.5

    def test_no_overlap(self) -> None:
        p, r = _precision_recall({"a"}, {"b"})
        assert p == 0.0
        assert r == 0.0

    def test_empty_expected(self) -> None:
        p, r = _precision_recall({"a"}, set())
        assert p == 0.0
        assert r == 1.0

    def test_both_empty(self) -> None:
        p, r = _precision_recall(set(), set())
        assert p == 1.0
        assert r == 1.0

    def test_empty_predicted(self) -> None:
        p, r = _precision_recall(set(), {"a"})
        assert p == 0.0
        assert r == 0.0


class TestGoldenDataset:
    def test_has_20_cases(self) -> None:
        assert len(GOLDEN_DATASET) == 20

    def test_all_cases_have_ids(self) -> None:
        for case in GOLDEN_DATASET:
            assert case.id.startswith("case_")

    def test_all_cases_have_descriptions(self) -> None:
        for case in GOLDEN_DATASET:
            assert len(case.description) > 10


class TestEvaluateCase:
    def test_evaluates_case_01(self) -> None:
        case = GOLDEN_DATASET[0]  # B2B SaaS
        result = evaluate_case(case)
        assert isinstance(result, EvalResult)
        assert result.case_id == "case_01"
        assert 0.0 <= result.trigger_precision <= 1.0
        assert 0.0 <= result.trigger_recall <= 1.0

    def test_evaluates_minimal_service(self) -> None:
        case = GOLDEN_DATASET[10]  # Minimal service
        result = evaluate_case(case)
        assert result.trigger_precision == 1.0
        assert result.trigger_recall == 1.0

    def test_evaluates_case_with_llm_extractor(self) -> None:
        case = GOLDEN_DATASET[0]  # B2B SaaS

        def llm_fn(_system_prompt: str, user_prompt: str) -> str:
            assert case.description in user_prompt
            return json.dumps(
                {
                    "architecture_type": case.expected_architecture_type,
                    "data_categories": case.expected_data_categories,
                    "storage_location": "russia",
                    "admin_access": {
                        "exists": True,
                        "exposed_to_internet": True,
                        "mfa_enabled": False,
                    },
                }
            )

        result = evaluate_case(case, llm_fn=llm_fn)

        assert result.architecture_type_match is True
        assert result.category_precision == 1.0
        assert result.category_recall == 1.0


class TestRunEvaluation:
    def test_returns_aggregate_metrics(self) -> None:
        report = run_evaluation()
        assert report["n_cases"] == 20
        assert 0.0 <= report["avg_architecture_type_accuracy"] <= 1.0
        assert 0.0 <= report["avg_trigger_precision"] <= 1.0
        assert 0.0 <= report["avg_trigger_recall"] <= 1.0
        assert 0.0 <= report["avg_category_precision"] <= 1.0
        assert 0.0 <= report["avg_category_recall"] <= 1.0
        assert 0.0 <= report["avg_citation_coverage"] <= 1.0
        assert isinstance(report["total_false_positives"], int)
        assert isinstance(report["total_false_negatives"], int)
        assert len(report["results"]) == 20

    def test_run_evaluation_accepts_llm_extractor(self) -> None:
        def llm_fn(_system_prompt: str, user_prompt: str) -> str:
            case = next(case for case in GOLDEN_DATASET if case.description in user_prompt)
            return json.dumps(
                {
                    "architecture_type": case.expected_architecture_type,
                    "data_categories": case.expected_data_categories,
                    "has_payments": case.expected_has_payments,
                    "has_electronic_signature": case.expected_has_electronic_signature,
                }
            )

        report = run_evaluation(llm_fn=llm_fn)

        assert report["avg_architecture_type_accuracy"] == 1.0
