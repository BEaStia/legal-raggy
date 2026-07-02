"""Run evaluation over the golden dataset and print results."""

import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.evaluation.metrics import run_evaluation


def main() -> None:
    """Run evaluation and print report."""
    results = run_evaluation()

    print("=" * 60)
    print("EVALUATION REPORT")
    print("=" * 60)
    print()
    print(f"Cases evaluated: {results['n_cases']}")
    print()
    print("AGGREGATE METRICS:")
    print(f"  Trigger Precision:     {results['avg_trigger_precision']:.3f}")
    print(f"  Trigger Recall:        {results['avg_trigger_recall']:.3f}")
    print(f"  Category Precision:    {results['avg_category_precision']:.3f}")
    print(f"  Category Recall:       {results['avg_category_recall']:.3f}")
    print(f"  Citation Coverage:     {results['avg_citation_coverage']:.3f}")
    print(f"  Total False Positives: {results['total_false_positives']}")
    print(f"  Total False Negatives: {results['total_false_negatives']}")
    print()
    print("PER-CASE RESULTS:")
    for r in results["results"]:
        print(f"  [{r.case_id}]")
        print(f"    Trigger P/R: {r.trigger_precision:.2f} / {r.trigger_recall:.2f}")
        print(f"    Category P/R: {r.category_precision:.2f} / {r.category_recall:.2f}")
        print(f"    Citation Coverage: {r.citation_coverage:.2f}")
        if r.false_positives:
            print(f"    FP: {r.false_positives}")
        if r.false_negatives:
            print(f"    FN: {r.false_negatives}")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
