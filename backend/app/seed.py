from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.completion import Achievement
from app.models.room import Room
from app.models.task import Task
from app.models.user import User


async def seed_data(db: AsyncSession) -> None:
    """Erstellt Beispiel-Daten, wenn die DB leer ist."""
    existing = await db.execute(select(User).limit(1))
    if existing.scalar_one_or_none():
        # Achievements nachladen falls nötig
        await _seed_achievements(db)
        await db.commit()
        return

    # Benutzer
    lukas = User(username="lukas", display_name="Lukas")
    eva = User(username="eva", display_name="Eva")
    db.add_all([lukas, eva])

    # Räume
    rooms = [
        Room(name="Küche", icon="mdi:silverware-fork-knife", sort_order=1),
        Room(name="Wohnzimmer", icon="mdi:sofa", sort_order=2),
        Room(name="Schlafzimmer", icon="mdi:bed", sort_order=3),
        Room(name="Bad", icon="mdi:shower", sort_order=4),
        Room(name="Ankleide", icon="mdi:wardrobe", sort_order=5),
        Room(name="Flur", icon="mdi:door", sort_order=6),
    ]
    db.add_all(rooms)
    await db.flush()

    # Room-IDs holen
    room_map = {r.name: r.id for r in rooms}

    # Tasks
    tasks = [
        Task(title="Spülmaschine ausräumen", room_id=room_map["Küche"], base_points=10, estimated_minutes=10, recurrence="daily"),
        Task(title="Kühlschrank reinigen", room_id=room_map["Küche"], base_points=25, estimated_minutes=30, recurrence="weekly", recurrence_day=6),
        Task(title="Bett machen", room_id=room_map["Schlafzimmer"], base_points=5, estimated_minutes=5, recurrence="daily"),
        Task(title="Bettwäsche wechseln", room_id=room_map["Schlafzimmer"], base_points=20, estimated_minutes=20, recurrence="weekly", recurrence_day=0),
        Task(title="Toilette putzen", room_id=room_map["Bad"], base_points=20, estimated_minutes=15, recurrence="weekly", recurrence_day=3),
        Task(title="Handtücher wechseln", room_id=room_map["Bad"], base_points=10, estimated_minutes=10, recurrence="weekly", recurrence_day=3),
        Task(title="Wäsche einräumen", room_id=room_map["Ankleide"], base_points=10, estimated_minutes=15, recurrence="daily"),
        Task(title="Aufräumen", room_id=room_map["Ankleide"], base_points=15, estimated_minutes=20, recurrence="weekly", recurrence_day=5),
    ]
    db.add_all(tasks)

    # Achievements
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
