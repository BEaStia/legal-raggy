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

from scripts.fetch_laws import LAW_IDS, LawFetchResult, fetch_law  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)

LOG_DIR = PROJECT_ROOT / "data" / "logs"


def _notification_for(result: LawFetchResult) -> str | None:
    """Build a human-readable notification line for important update events."""
    key = result["key"]
    if result["status"] == "changed":
        version = result.get("version_date", "unknown")
        return f"{key} changed to version {version}"
    if result["status"] == "failed":
        error = result.get("error", "unknown error")
        return f"{key} failed: {error}"
    return None


def run_update(force: bool = False) -> dict:
    """Fetch all laws and return summary."""
    results: dict = {
        "started_at": datetime.now().isoformat(),
        "laws": [],
        "errors": [],
        "notifications": [],
    }

    for key in LAW_IDS:
        try:
            result = fetch_law(key, force=force)
        except Exception as e:
            logger.error("Failed to update %s: %s", key, e)
            result = {
                "key": key,
                "status": "failed",
                "changed": False,
                "error": str(e),
            }

        results["laws"].append(result)

        if result["status"] == "failed":
            error = result.get("error", "unknown error")
            logger.error("Failed to update %s: %s", key, error)
            results["errors"].append({"key": key, "error": error})

        notification = _notification_for(result)
        if notification is not None:
            results["notifications"].append(notification)

    results["completed_at"] = datetime.now().isoformat()
    results["total"] = len(LAW_IDS)
    results["changed"] = sum(1 for law in results["laws"] if law["status"] == "changed")
    results["skipped"] = sum(1 for law in results["laws"] if law["status"] == "skipped")
    results["failed"] = len(results["errors"])
    results["ok"] = results["total"] - results["failed"]

    return results


def _write_update_log(results: dict) -> Path:
    """Persist a JSON update log and return its path."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"laws_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    log_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return log_file


def main() -> None:
    """Run update and log results."""
    force = "--force" in sys.argv

    logger.info("Starting laws update (force=%s)", force)

    results = run_update(force=force)

    # Write log
    log_file = _write_update_log(results)

    logger.info(
        "Update complete: %d/%d ok, %d changed, %d skipped, %d failed. Log: %s",
        results["ok"],
        results["total"],
        results["changed"],
        results["skipped"],
        results["failed"],
        log_file,
    )

    for notification in results["notifications"]:
        logger.warning("Notification: %s", notification)

    if results["failed"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
