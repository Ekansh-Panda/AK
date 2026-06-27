"""Background task scheduler (APScheduler)."""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Single global instance of the scheduler
_scheduler: Any = None


def start_scheduler() -> None:
    """Start the APScheduler if SCHEDULER_ENABLED is True."""
    global _scheduler
    if not settings.SCHEDULER_ENABLED:
        logger.info("Scheduler disabled via config (SCHEDULER_ENABLED=False)")
        return

    # Delay import to avoid pulling it in when disabled
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.interval import IntervalTrigger

    _scheduler = AsyncIOScheduler()
    
    # Register some default maintenance jobs if needed
    _scheduler.add_job(
        _maintenance_task,
        trigger=IntervalTrigger(hours=24),
        id="daily_maintenance",
        replace_existing=True,
    )
    
    _scheduler.start()
    logger.info("Scheduler started successfully")


def shutdown_scheduler() -> None:
    """Shut down the scheduler if it is running."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler shut down")
    _scheduler = None


async def _maintenance_task() -> None:
    """A background maintenance task."""
    logger.info("Running daily maintenance task...")
    await asyncio.sleep(1)
    logger.info("Daily maintenance complete.")


def schedule_task_reminder(task_id: str, due_at: datetime) -> None:
    """Schedule a reminder/notification when a task is due."""
    if not _scheduler or not getattr(_scheduler, "running", False):
        return

    from apscheduler.triggers.date import DateTrigger

    job_id = f"task_{task_id}_due"
    
    # If the due date is in the past, don't schedule
    if due_at <= datetime.now(due_at.tzinfo):
        logger.debug("Task %s due_at is in the past, skipping schedule", task_id)
        return

    _scheduler.add_job(
        _task_due_callback,
        trigger=DateTrigger(run_date=due_at),
        args=[task_id],
        id=job_id,
        replace_existing=True,
    )
    logger.debug("Scheduled reminder for task %s at %s", task_id, due_at)

def cancel_task_reminder(task_id: str) -> None:
    """Cancel a scheduled task reminder."""
    if not _scheduler or not getattr(_scheduler, "running", False):
        return
    job_id = f"task_{task_id}_due"
    if _scheduler.get_job(job_id):
        _scheduler.remove_job(job_id)
        logger.debug("Cancelled reminder for task %s", task_id)


async def _task_due_callback(task_id: str) -> None:
    """Fired when a task reaches its due_at timestamp."""
    logger.info("Task %s is due!", task_id)
    
    # In a full implementation, this might broadcast a WS message to the UI
    # or send a push notification. For Phase 5, we'll log it and broadcast to /ws/status
    try:
        from app.ws import manager
        await manager.broadcast("status", {
            "type": "notification",
            "title": "Task Due",
            "message": f"Task {task_id} is due now.",
        })
    except Exception as exc:
        logger.error("Failed to broadcast task due notification: %s", exc)
