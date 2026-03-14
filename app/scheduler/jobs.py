"""
scheduler/jobs.py
─────────────────
APScheduler integration for periodic environment-data collection.

Uses ``AsyncIOScheduler`` to run the updater every 10 minutes.
The scheduler is started/stopped via the FastAPI lifespan context.
"""

from __future__ import annotations

import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.services.updater import update_all_environmental_data, prune_old_data

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def _run_updater() -> None:
    """Bridge sync APScheduler callback → async updater coroutine."""
    loop = asyncio.get_event_loop()
    loop.create_task(update_all_environmental_data())


def _run_pruner() -> None:
    """Bridge sync APScheduler callback → async pruner coroutine."""
    loop = asyncio.get_event_loop()
    loop.create_task(prune_old_data())


def start_scheduler() -> None:
    """Register jobs and start the scheduler.

    Called once during application startup (via FastAPI lifespan).
    """
    scheduler.add_job(
        _run_updater,
        trigger=IntervalTrigger(minutes=10),
        id="env_data_updater",
        name="Fetch & store environment data",
        replace_existing=True,
    )
    scheduler.add_job(
        _run_pruner,
        trigger=IntervalTrigger(days=1),
        id="env_data_pruner",
        name="Prune old environment data",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started — fetch runs every 10 min, prune runs daily.")


def stop_scheduler() -> None:
    """Gracefully shut down the scheduler.

    Called during application shutdown (via FastAPI lifespan).
    """
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped.")
