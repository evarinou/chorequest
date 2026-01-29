from datetime import date

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskInstance


async def generate_task_instances_for_date(db: AsyncSession, target_date: date) -> int:
    """Erstellt Task-Instanzen für alle aktiven Tasks am gegebenen Datum."""
    created_count = 0
    weekday = target_date.weekday()  # 0=Montag, 6=Sonntag
    day_of_month = target_date.day

    # Alle aktiven Tasks laden
    result = await db.execute(select(Task).where(Task.is_active == True))  # noqa: E712
    tasks = result.scalars().all()

    for task in tasks:
        should_create = False

        if task.recurrence == "daily":
            should_create = True
        elif task.recurrence == "weekly":
            should_create = (task.recurrence_day == weekday)
        elif task.recurrence == "monthly":
            should_create = (task.recurrence_day == day_of_month)
        elif task.recurrence == "once":
            # Einmalige Tasks: nur erstellen wenn noch keine Instanz existiert
            existing = await db.execute(
                select(func.count(TaskInstance.id))
                .where(TaskInstance.task_id == task.id)
            )
            if existing.scalar() == 0:
                should_create = True

        if not should_create:
            continue

        # Duplikat-Prüfung: Gibt es schon eine Instanz für diesen Task und Tag?
        existing = await db.execute(
            select(func.count(TaskInstance.id))
            .where(TaskInstance.task_id == task.id)
            .where(TaskInstance.due_date == target_date)
        )
        if existing.scalar() > 0:
            continue

        instance = TaskInstance(
            task_id=task.id,
            due_date=target_date,
            status="pending",
        )
        db.add(instance)
        created_count += 1

    return created_count
