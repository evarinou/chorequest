import logging
from datetime import date

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import settings
from app.database import async_session

logger = logging.getLogger("chorequest.scheduler")

scheduler = AsyncIOScheduler(timezone=settings.timezone)


async def _generate_daily_tasks():
    """Erstellt Task-Instanzen für den heutigen Tag."""
    from app.services.task_service import generate_task_instances_for_date

    today = date.today()
    async with async_session() as db:
        count = await generate_task_instances_for_date(db, today)
        await db.commit()
    logger.info("Tägliche Task-Generierung: %d Instanzen erstellt für %s", count, today)


async def _reset_weekly_points():
    """Setzt die wöchentlichen Punkte aller User zurück (Sonntags)."""
    from sqlalchemy import select, update
    from app.models.user import User
    from app.services.achievement_service import check_and_unlock_achievements

    async with async_session() as db:
        # Vorher Weekly-Winner-Achievement prüfen
        result = await db.execute(select(User).order_by(User.weekly_points.desc()))
        users = result.scalars().all()

        for user in users:
            await check_and_unlock_achievements(db, user)

        # Weekly Points auf 0 setzen
        await db.execute(update(User).values(weekly_points=0))
        await db.commit()

    logger.info("Wöchentliche Punkte zurückgesetzt")


async def _generate_weekly_summary():
    """Generiert die wöchentliche KI-Zusammenfassung (Sonntags vor dem Reset)."""
    from app.services.claude_service import generate_weekly_summary

    async with async_session() as db:
        summary, tokens_used = await generate_weekly_summary(db)
        await db.commit()

    kw = summary.week_start.isocalendar()[1]
    logger.info("Wöchentliche KI-Zusammenfassung KW %d generiert (%d Tokens)", kw, tokens_used)


async def _check_overdue_tasks():
    """Prüft und loggt überfällige Tasks."""
    from sqlalchemy import select, func
    from app.models.task import TaskInstance

    today = date.today()
    async with async_session() as db:
        result = await db.execute(
            select(func.count(TaskInstance.id))
            .where(TaskInstance.due_date < today)
            .where(TaskInstance.status == "pending")
        )
        overdue_count = result.scalar() or 0

    if overdue_count > 0:
        logger.warning("Überfällige Tasks: %d", overdue_count)


def start_scheduler():
    """Startet den APScheduler mit allen geplanten Jobs."""
    # Täglich um 00:05 Task-Instanzen generieren
    scheduler.add_job(
        _generate_daily_tasks,
        CronTrigger(hour=0, minute=5, timezone=settings.timezone),
        id="generate_daily_tasks",
        replace_existing=True,
    )

    # Sonntag 19:00: Wöchentliche KI-Zusammenfassung generieren
    scheduler.add_job(
        _generate_weekly_summary,
        CronTrigger(day_of_week="sun", hour=19, minute=0, timezone=settings.timezone),
        id="generate_weekly_summary",
        replace_existing=True,
    )

    # Sonntag 20:00: Weekly Points zurücksetzen
    scheduler.add_job(
        _reset_weekly_points,
        CronTrigger(day_of_week="sun", hour=20, minute=0, timezone=settings.timezone),
        id="reset_weekly_points",
        replace_existing=True,
    )

    # Stündlich: Überfällige Tasks prüfen
    scheduler.add_job(
        _check_overdue_tasks,
        CronTrigger(minute=0, timezone=settings.timezone),
        id="check_overdue_tasks",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler gestartet mit %d Jobs", len(scheduler.get_jobs()))


def stop_scheduler():
    """Stoppt den Scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler gestoppt")
