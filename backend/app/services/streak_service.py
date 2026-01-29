from datetime import date, timedelta

from sqlalchemy import select, func, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.completion import TaskCompletion
from app.models.user import User
from app.schemas.task import StreakUpdate


def get_streak_bonus_multiplier(streak_days: int) -> float:
    """Gibt den Streak-Bonus-Multiplikator zurück."""
    if streak_days >= 7:
        return 1.25
    elif streak_days >= 3:
        return 1.1
    return 1.0


async def update_user_streak(db: AsyncSession, user: User) -> StreakUpdate:
    """Aktualisiert den Streak eines Benutzers basierend auf aufeinanderfolgenden Tagen."""
    today = date.today()

    # Alle Tage mit Completions für diesen User, absteigend sortiert
    result = await db.execute(
        select(distinct(func.date(TaskCompletion.completed_at)))
        .where(TaskCompletion.user_id == user.id)
        .order_by(func.date(TaskCompletion.completed_at).desc())
    )
    completion_dates = [row[0] for row in result.all()]

    if not completion_dates:
        user.current_streak = 0
        return StreakUpdate(
            current_streak=0,
            longest_streak=user.longest_streak,
            streak_bonus_active=False,
        )

    # Streak berechnen: aufeinanderfolgende Tage rückwärts von heute
    streak = 0
    expected_date = today

    for d in completion_dates:
        if d == expected_date:
            streak += 1
            expected_date -= timedelta(days=1)
        elif d < expected_date:
            # Lücke gefunden
            break

    user.current_streak = streak
    if streak > user.longest_streak:
        user.longest_streak = streak

    return StreakUpdate(
        current_streak=user.current_streak,
        longest_streak=user.longest_streak,
        streak_bonus_active=get_streak_bonus_multiplier(streak) > 1.0,
    )
