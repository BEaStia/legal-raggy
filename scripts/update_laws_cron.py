#!/usr/bin/env python3
"""Cron job to auto-update laws corpus.

Runs fetch_laws.py with change detection, logs results,
and exits with appropriate status code for cron monitoring.

Usage:
    python scripts/update_laws_cron.py          # update all laws
    python scripts/update_laws_cron.py --force  # force re-fetch all
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.fetch_laws import LAW_IDS, fetch_law

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)

LOG_DIR = PROJECT_ROOT / "data" / "logs"


def run_update(force: bool = False) -> dict:
    """Fetch all laws and return summary."""
    results = {"started_at": datetime.now().isoformat(), "laws": [], "errors": []}

    for key in LAW_IDS:
        try:
            fetch_law(key, force=force)
            results["laws"].append({"key": key, "status": "ok"})
        except Exception as e:
            logger.error("Failed to update %s: %s", key, e)
            results["errors"].append({"key": key, "error": str(e)})
            results["laws"].append({"key": key, "status": "error"})

    results["completed_at"] = datetime.now().isoformat()
    results["total"] = len(LAW_IDS)
    results["ok"] = sum(1 for l in results["laws"] if l["status"] == "ok")
    results["failed"] = len(results["errors"])

    return results


def main() -> None:
    """Run update and log results."""
    force = "--force" in sys.argv

    logger.info("Starting laws update (force=%s)", force)

    results = run_update(force=force)

    # Write log
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"laws_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    log_file.write_text(json.dumps(results, indent=2), encoding="utf-8")

    logger.info(
        "Update complete: %d/%d ok, %d failed. Log: %s",
        results["ok"],
        results["total"],
        results["failed"],
        log_file,
    )

    if results["failed"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
