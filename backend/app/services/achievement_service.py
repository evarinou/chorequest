from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.completion import Achievement, TaskCompletion, UserAchievement
from app.models.task import Task
from app.models.user import User
from app.schemas.task import UnlockedAchievement


async def _get_total_completions(db: AsyncSession, user_id: int) -> int:
    result = await db.execute(
        select(func.count(TaskCompletion.id)).where(TaskCompletion.user_id == user_id)
    )
    return result.scalar() or 0


async def _get_room_completions(db: AsyncSession, user_id: int, room_id: int) -> int:
    result = await db.execute(
        select(func.count(TaskCompletion.id))
        .join(
            Task,
            TaskCompletion.task_instance.has(task_id=Task.id),
        )
        .where(TaskCompletion.user_id == user_id)
    )
    # Besser: über task_instances joinen
    from app.models.task import TaskInstance
    result = await db.execute(
        select(func.count(TaskCompletion.id))
        .join(TaskInstance, TaskCompletion.task_instance_id == TaskInstance.id)
        .join(Task, TaskInstance.task_id == Task.id)
        .where(TaskCompletion.user_id == user_id)
        .where(Task.room_id == room_id)
    )
    return result.scalar() or 0


async def _check_criteria(db: AsyncSession, user: User, criteria: dict) -> tuple[bool, int, int]:
    """Prüft ob ein Achievement-Kriterium erfüllt ist. Gibt (erfüllt, aktuell, ziel) zurück."""
    criteria_type = criteria.get("type")
    target = criteria.get("value", 0)

    if criteria_type == "total_tasks":
        current = await _get_total_completions(db, user.id)
        return current >= target, current, target

    elif criteria_type == "room_tasks":
        room_id = criteria.get("room_id")
        if room_id:
            current = await _get_room_completions(db, user.id, room_id)
        else:
            # Beliebiger Raum - höchste Anzahl
            from app.models.task import TaskInstance
            result = await db.execute(
                select(Task.room_id, func.count(TaskCompletion.id).label("cnt"))
                .join(TaskInstance, TaskCompletion.task_instance_id == TaskInstance.id)
                .join(Task, TaskInstance.task_id == Task.id)
                .where(TaskCompletion.user_id == user.id)
                .group_by(Task.room_id)
                .order_by(func.count(TaskCompletion.id).desc())
                .limit(1)
            )
            row = result.first()
            current = row.cnt if row else 0
        return current >= target, current, target

    elif criteria_type == "streak":
        current = user.current_streak
        return current >= target, current, target

    elif criteria_type == "weekly_winner":
        # Prüft ob der User die meisten Weekly-Points hat
        from sqlalchemy import and_
        result = await db.execute(
            select(User.id)
            .order_by(User.weekly_points.desc())
            .limit(1)
        )
        winner_id = result.scalar()
        is_winner = winner_id == user.id and user.weekly_points > 0
        return is_winner, 1 if is_winner else 0, 1

    return False, 0, 0


async def check_and_unlock_achievements(
    db: AsyncSession, user: User
) -> list[UnlockedAchievement]:
    """Prüft alle Achievements und schaltet neue frei."""
    # Bereits freigeschaltete Achievements
    result = await db.execute(
        select(UserAchievement.achievement_id).where(UserAchievement.user_id == user.id)
    )
    unlocked_ids = set(result.scalars().all())

    # Alle Achievements laden
    result = await db.execute(select(Achievement))
    all_achievements = result.scalars().all()

    newly_unlocked = []

    for achievement in all_achievements:
        if achievement.id in unlocked_ids:
            continue

        fulfilled, _, _ = await _check_criteria(db, user, achievement.criteria)
        if fulfilled:
            user_achievement = UserAchievement(
                user_id=user.id,
                achievement_id=achievement.id,
                unlocked_at=datetime.utcnow(),
            )
            db.add(user_achievement)

            # Bonus-Punkte gutschreiben
            user.total_points += achievement.points_reward
            user.weekly_points += achievement.points_reward

            newly_unlocked.append(UnlockedAchievement(
                id=achievement.id,
                name=achievement.name,
                description=achievement.description,
                icon=achievement.icon,
                points_reward=achievement.points_reward,
            ))

    return newly_unlocked


async def get_achievement_progress(
    db: AsyncSession, user: User
) -> list[dict]:
    """Gibt den Fortschritt für alle Achievements zurück."""
    # Bereits freigeschaltete
    result = await db.execute(
        select(UserAchievement).where(UserAchievement.user_id == user.id)
    )
    unlocked_map = {ua.achievement_id: ua.unlocked_at for ua in result.scalars().all()}

    # Alle Achievements
    result = await db.execute(select(Achievement))
    all_achievements = result.scalars().all()

    progress_list = []
    for achievement in all_achievements:
        _, current, target = await _check_criteria(db, user, achievement.criteria)
        target = max(target, 1)  # Division durch 0 vermeiden
        progress_list.append({
            "achievement": achievement,
            "unlocked": achievement.id in unlocked_map,
            "unlocked_at": unlocked_map.get(achievement.id),
            "current_value": current,
            "target_value": target,
            "progress_percent": min(100.0, round(current / target * 100, 1)),
        })

    return progress_list
