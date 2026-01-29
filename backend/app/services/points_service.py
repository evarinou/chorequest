from datetime import date, datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.completion import TaskCompletion
from app.models.room import Room
from app.models.task import Task, TaskInstance
from app.models.user import User
from app.schemas.task import BonusBreakdown


async def check_room_completion(db: AsyncSession, room_id: int, target_date: date) -> bool:
    """Prüft ob alle Tasks eines Raums am gegebenen Tag erledigt sind."""
    # Alle Instanzen des Raums für den Tag
    total_result = await db.execute(
        select(func.count(TaskInstance.id))
        .join(Task)
        .where(Task.room_id == room_id)
        .where(TaskInstance.due_date == target_date)
    )
    total = total_result.scalar() or 0

    if total == 0:
        return False

    # Erledigte Instanzen (inkl. der aktuellen, die gerade completed wird)
    completed_result = await db.execute(
        select(func.count(TaskInstance.id))
        .join(Task)
        .where(Task.room_id == room_id)
        .where(TaskInstance.due_date == target_date)
        .where(TaskInstance.status == "completed")
    )
    completed = completed_result.scalar() or 0

    return completed >= total


async def calculate_points(
    db: AsyncSession,
    task: Task,
    room: Room,
    user: User,
    completion_time: datetime,
) -> BonusBreakdown:
    """Berechnet Punkte mit allen Boni."""
    base_points = task.base_points
    room_multiplier = float(room.point_multiplier)

    # Frühbonus: +20% wenn vor 12:00
    early_bonus = 0.2 if completion_time.hour < 12 else 0.0

    # Streak-Bonus
    from app.services.streak_service import get_streak_bonus_multiplier
    streak_multiplier = get_streak_bonus_multiplier(user.current_streak)
    streak_bonus = streak_multiplier - 1.0  # z.B. 1.1 -> 0.1

    # Raum-Completion-Bonus: +50% wenn alle Tasks des Raums erledigt
    today = completion_time.date()
    room_complete = await check_room_completion(db, room.id, today)
    room_completion_bonus = 0.5 if room_complete else 0.0

    # Gesamtberechnung
    total_multiplier = room_multiplier * (1.0 + early_bonus + streak_bonus + room_completion_bonus)
    total_points = round(base_points * total_multiplier)
    bonus_points = total_points - base_points

    return BonusBreakdown(
        base_points=base_points,
        room_multiplier=room_multiplier,
        early_bonus=early_bonus,
        streak_bonus=streak_bonus,
        room_completion_bonus=room_completion_bonus,
        total_points=total_points,
        bonus_points=max(0, bonus_points),
    )
