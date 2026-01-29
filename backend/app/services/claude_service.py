import json
import logging
import re
from datetime import date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.completion import Achievement, TaskCompletion, UserAchievement, WeeklySummary
from app.models.room import Room
from app.models.task import Task, TaskInstance
from app.models.user import User

logger = logging.getLogger("chorequest.claude")

SYSTEM_PROMPT = """Du bist der KI-Assistent von ChoreQuest, einem gamifizierten Haushalts-Todo-Manager.
Erstelle eine motivierende Wochen-Zusammenfassung auf Deutsch.

Antworte AUSSCHLIESSLICH mit validem JSON in folgendem Format:
{
  "summary_text": "Deine motivierende Zusammenfassung als Fließtext. Verwende Absätze (getrennt durch \\n\\n) für bessere Lesbarkeit. Erwähne Highlights, Streaks und ermutige die Nutzer.",
  "suggested_tasks": [
    {
      "title": "Aufgaben-Titel",
      "description": "Kurze Beschreibung",
      "room_name": "Raumname",
      "estimated_minutes": 15,
      "reason": "Warum diese Aufgabe vorgeschlagen wird"
    }
  ]
}

Regeln:
- Zusammenfassung soll motivierend und positiv sein, aber auch ehrlich
- Nenne konkrete Zahlen und Erfolge
- Schlage 2-4 Aufgaben vor basierend auf den Statistiken (z.B. vernachlässigte Räume)
- Schreibe alles auf Deutsch
- Nur valides JSON ausgeben, kein Markdown, keine Erklärungen"""


async def gather_weekly_stats(
    db: AsyncSession, week_start: date, week_end: date
) -> dict:
    """Sammelt Statistiken für die angegebene Woche."""
    # User-Daten
    users_result = await db.execute(select(User))
    users = users_result.scalars().all()

    user_stats = []
    for user in users:
        # Completions dieser Woche
        completions_result = await db.execute(
            select(
                func.count(TaskCompletion.id),
                func.coalesce(func.sum(TaskCompletion.points_earned), 0),
            )
            .where(TaskCompletion.user_id == user.id)
            .where(TaskCompletion.completed_at >= datetime.combine(week_start, datetime.min.time()))
            .where(TaskCompletion.completed_at < datetime.combine(week_end + timedelta(days=1), datetime.min.time()))
        )
        row = completions_result.one()
        user_stats.append({
            "name": user.display_name or user.username,
            "completions": row[0],
            "points_earned": int(row[1]),
            "current_streak": user.current_streak,
            "weekly_points": user.weekly_points,
        })

    # Raum-Statistiken
    rooms_result = await db.execute(select(Room))
    rooms = rooms_result.scalars().all()

    room_stats = []
    for room in rooms:
        # Task-Instanzen dieser Woche pro Raum
        instances_result = await db.execute(
            select(TaskInstance.status, func.count(TaskInstance.id))
            .join(Task, TaskInstance.task_id == Task.id)
            .where(Task.room_id == room.id)
            .where(TaskInstance.due_date >= week_start)
            .where(TaskInstance.due_date <= week_end)
            .group_by(TaskInstance.status)
        )
        status_counts = {row[0]: row[1] for row in instances_result.all()}
        room_stats.append({
            "name": room.name,
            "completed": status_counts.get("completed", 0),
            "pending": status_counts.get("pending", 0),
            "skipped": status_counts.get("skipped", 0),
        })

    # Achievements dieser Woche
    achievements_result = await db.execute(
        select(Achievement.name, User.display_name, User.username)
        .join(UserAchievement, UserAchievement.achievement_id == Achievement.id)
        .join(User, UserAchievement.user_id == User.id)
        .where(UserAchievement.unlocked_at >= datetime.combine(week_start, datetime.min.time()))
        .where(UserAchievement.unlocked_at < datetime.combine(week_end + timedelta(days=1), datetime.min.time()))
    )
    achievements = [
        {"achievement": row[0], "user": row[1] or row[2]}
        for row in achievements_result.all()
    ]

    # Gesamtstatistik
    total_instances_result = await db.execute(
        select(func.count(TaskInstance.id))
        .where(TaskInstance.due_date >= week_start)
        .where(TaskInstance.due_date <= week_end)
    )
    total_instances = total_instances_result.scalar() or 0

    completed_instances_result = await db.execute(
        select(func.count(TaskInstance.id))
        .where(TaskInstance.due_date >= week_start)
        .where(TaskInstance.due_date <= week_end)
        .where(TaskInstance.status == "completed")
    )
    completed_instances = completed_instances_result.scalar() or 0

    completion_rate = (
        round(completed_instances / total_instances * 100, 1) if total_instances > 0 else 0
    )

    return {
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "users": user_stats,
        "rooms": room_stats,
        "achievements_unlocked": achievements,
        "total_tasks": total_instances,
        "completed_tasks": completed_instances,
        "completion_rate_percent": completion_rate,
    }


async def call_claude_api(stats: dict) -> tuple[str, list[dict], int]:
    """Ruft die Claude API auf und gibt (summary_text, suggested_tasks, tokens_used) zurück."""
    import anthropic

    client = anthropic.AsyncAnthropic(api_key=settings.claude_api_key)

    response = await client.messages.create(
        model=settings.claude_model,
        max_tokens=1500,
        temperature=0.7,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": json.dumps(stats, ensure_ascii=False)}
        ],
    )

    raw_text = response.content[0].text
    tokens_used = (response.usage.input_tokens or 0) + (response.usage.output_tokens or 0)

    # JSON parsen (Markdown-Codeblöcke strippen falls vorhanden)
    cleaned = re.sub(r"^```(?:json)?\s*\n?", "", raw_text.strip())
    cleaned = re.sub(r"\n?```\s*$", "", cleaned)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        logger.warning("Claude-Antwort konnte nicht als JSON geparst werden: %s", raw_text[:200])
        return raw_text, [], tokens_used

    summary_text = data.get("summary_text", raw_text)
    suggested_tasks = data.get("suggested_tasks", [])

    return summary_text, suggested_tasks, tokens_used


async def generate_weekly_summary(
    db: AsyncSession, week_start: date | None = None
) -> tuple[WeeklySummary, int]:
    """Generiert eine Wochen-Zusammenfassung und speichert sie in der DB."""
    # Montag der aktuellen/angegebenen Woche berechnen
    if week_start is None:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())  # Montag

    week_end = week_start + timedelta(days=6)  # Sonntag

    # Bestehende Summary für diese Woche löschen (für Re-Generierung)
    existing_result = await db.execute(
        select(WeeklySummary).where(WeeklySummary.week_start == week_start)
    )
    existing = existing_result.scalar_one_or_none()
    if existing:
        await db.delete(existing)
        await db.flush()

    # Stats sammeln
    stats = await gather_weekly_stats(db, week_start, week_end)

    tokens_used = 0
    summary_text = ""
    suggested_tasks: list[dict] = []

    if not settings.claude_api_key:
        # Fallback ohne API-Key
        logger.info("Kein Claude API-Key konfiguriert, verwende Fallback-Text")
        summary_text = (
            f"Wochen-Zusammenfassung KW {week_start.isocalendar()[1]}\n\n"
            f"In dieser Woche wurden {stats['completed_tasks']} von {stats['total_tasks']} "
            f"Aufgaben erledigt ({stats['completion_rate_percent']}%).\n\n"
            "Für eine KI-generierte Zusammenfassung bitte den Claude API-Key konfigurieren."
        )
    else:
        try:
            summary_text, suggested_tasks, tokens_used = await call_claude_api(stats)
        except Exception as e:
            logger.error("Fehler beim Claude API-Aufruf: %s", e)
            summary_text = (
                f"Wochen-Zusammenfassung KW {week_start.isocalendar()[1]}\n\n"
                f"In dieser Woche wurden {stats['completed_tasks']} von {stats['total_tasks']} "
                f"Aufgaben erledigt ({stats['completion_rate_percent']}%).\n\n"
                f"Die KI-Zusammenfassung konnte nicht generiert werden: {e}"
            )

    summary = WeeklySummary(
        week_start=week_start,
        week_end=week_end,
        summary_text=summary_text,
        suggested_tasks=suggested_tasks if suggested_tasks else None,
        generated_at=datetime.utcnow(),
    )
    db.add(summary)
    await db.flush()
    await db.refresh(summary)

    logger.info(
        "Wochen-Zusammenfassung KW %d generiert (%d Tokens)",
        week_start.isocalendar()[1],
        tokens_used,
    )

    return summary, tokens_used
