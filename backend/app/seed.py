from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.completion import Achievement


async def seed_data(db: AsyncSession) -> None:
    """Erstellt Achievement-Definitionen beim ersten Start."""
    await _seed_achievements(db)
    await db.commit()


async def _seed_achievements(db: AsyncSession) -> None:
    """Erstellt Achievement-Definitionen falls noch nicht vorhanden."""
    existing = await db.execute(select(Achievement).limit(1))
    if existing.scalar_one_or_none():
        return

    achievements = [
        Achievement(
            name="Erste Schritte",
            description="Erledige deinen ersten Task",
            icon="mdi:flag-checkered",
            criteria={"type": "total_tasks", "value": 1},
            points_reward=25,
        ),
        Achievement(
            name="Fleißig",
            description="Erledige 50 Tasks insgesamt",
            icon="mdi:star",
            criteria={"type": "total_tasks", "value": 50},
            points_reward=100,
        ),
        Achievement(
            name="Putz-Profi",
            description="Erledige 100 Tasks insgesamt",
            icon="mdi:trophy",
            criteria={"type": "total_tasks", "value": 100},
            points_reward=250,
        ),
        Achievement(
            name="Küchenheld",
            description="Erledige 25 Tasks in der Küche",
            icon="mdi:chef-hat",
            criteria={"type": "room_tasks", "value": 25},
            points_reward=75,
        ),
        Achievement(
            name="Streak-Master",
            description="Halte einen Streak von 7 Tagen",
            icon="mdi:fire",
            criteria={"type": "streak", "value": 7},
            points_reward=150,
        ),
        Achievement(
            name="Wochensieger",
            description="Gewinne das wöchentliche Leaderboard",
            icon="mdi:crown",
            criteria={"type": "weekly_winner", "value": 1},
            points_reward=200,
        ),
    ]
    db.add_all(achievements)
