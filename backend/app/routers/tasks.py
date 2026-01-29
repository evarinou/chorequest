from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import verify_api_key
from app.database import get_db
from app.models.task import Task, TaskInstance
from app.models.room import Room
from app.models.completion import TaskCompletion
from app.models.user import User
from app.schemas.task import (
    AssignRequest,
    CompleteRequest,
    CompletionResponse,
    ExtendedCompletionResponse,
    TaskCreate,
    TaskInstanceResponse,
    TaskInstanceWithDetails,
    TaskResponse,
    TaskUpdate,
)
from app.services.points_service import calculate_points
from app.services.streak_service import update_user_streak
from app.services.achievement_service import check_and_unlock_achievements
from app.services.webhook_service import notify_task_completed, notify_achievement_unlocked

router = APIRouter(prefix="/api", tags=["Tasks"], dependencies=[Depends(verify_api_key)])


# === Task-Templates ===

@router.get("/tasks", response_model=list[TaskResponse])
async def list_tasks(
    room_id: int | None = None,
    is_active: bool | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Task)
    if room_id is not None:
        query = query.where(Task.room_id == room_id)
    if is_active is not None:
        query = query.where(Task.is_active == is_active)
    result = await db.execute(query.order_by(Task.title))
    return result.scalars().all()


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(data: TaskCreate, db: AsyncSession = Depends(get_db)):
    task = Task(**data.model_dump())
    db.add(task)
    await db.flush()
    await db.refresh(task)
    return task


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, data: TaskUpdate, db: AsyncSession = Depends(get_db)):
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task nicht gefunden")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    await db.flush()
    await db.refresh(task)
    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task nicht gefunden")
    await db.delete(task)


# === Task-Instanzen ===

@router.get("/instances", response_model=list[TaskInstanceWithDetails])
async def list_instances(
    room_id: int | None = None,
    user_id: int | None = None,
    task_status: str | None = Query(None, alias="status"),
    due_date: date | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(TaskInstance).options(
        selectinload(TaskInstance.task),
        selectinload(TaskInstance.assigned_user),
    )
    if room_id is not None:
        query = query.join(Task).where(Task.room_id == room_id)
    if user_id is not None:
        query = query.where(TaskInstance.assigned_user_id == user_id)
    if task_status is not None:
        query = query.where(TaskInstance.status == task_status)
    if due_date is not None:
        query = query.where(TaskInstance.due_date == due_date)
    result = await db.execute(query.order_by(TaskInstance.due_date))
    return result.scalars().all()


@router.get("/instances/today", response_model=list[TaskInstanceWithDetails])
async def list_today_instances(db: AsyncSession = Depends(get_db)):
    today = date.today()
    query = (
        select(TaskInstance)
        .options(
            selectinload(TaskInstance.task),
            selectinload(TaskInstance.assigned_user),
        )
        .where(TaskInstance.due_date == today)
        .where(TaskInstance.status == "pending")
        .order_by(TaskInstance.id)
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/instances/{instance_id}/complete", response_model=ExtendedCompletionResponse)
async def complete_instance(
    instance_id: int,
    data: CompleteRequest,
    db: AsyncSession = Depends(get_db),
):
    instance = await db.get(TaskInstance, instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Task-Instanz nicht gefunden")
    if instance.status != "pending":
        raise HTTPException(status_code=400, detail="Task ist nicht mehr offen")

    user = await db.get(User, data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")

    # Task und Raum laden
    task = await db.get(Task, instance.task_id)
    room = await db.get(Room, task.room_id)

    # Instanz als erledigt markieren
    instance.status = "completed"

    # Streak aktualisieren (vor Punkteberechnung, damit Streak-Bonus stimmt)
    streak_update = await update_user_streak(db, user)

    # Punkte berechnen mit allen Boni
    now = datetime.utcnow()
    bonus_breakdown = await calculate_points(db, task, room, user, now)

    # Completion erstellen
    completion = TaskCompletion(
        task_instance_id=instance_id,
        user_id=data.user_id,
        completed_at=now,
        points_earned=bonus_breakdown.total_points,
        bonus_points=bonus_breakdown.bonus_points,
        notes=data.notes,
    )
    db.add(completion)

    # Punkte dem User gutschreiben
    user.total_points += bonus_breakdown.total_points
    user.weekly_points += bonus_breakdown.total_points

    await db.flush()

    # Achievements prüfen (nach Punkteupdate)
    unlocked = await check_and_unlock_achievements(db, user)

    await db.refresh(completion)

    # Webhooks an Home Assistant senden (fire-and-forget)
    notify_task_completed(
        instance_id, task.title, user.display_name or user.username,
        bonus_breakdown.total_points, room.name,
    )
    for ach in unlocked:
        notify_achievement_unlocked(
            user.display_name or user.username, ach.name, ach.icon, ach.points_reward,
        )

    return ExtendedCompletionResponse(
        completion=CompletionResponse.model_validate(completion),
        bonus_breakdown=bonus_breakdown,
        streak=streak_update,
        unlocked_achievements=unlocked,
    )


@router.post("/instances/{instance_id}/skip", status_code=status.HTTP_200_OK)
async def skip_instance(instance_id: int, db: AsyncSession = Depends(get_db)):
    instance = await db.get(TaskInstance, instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Task-Instanz nicht gefunden")
    if instance.status != "pending":
        raise HTTPException(status_code=400, detail="Task ist nicht mehr offen")
    instance.status = "skipped"
    return {"detail": "Task übersprungen"}


@router.post("/instances/{instance_id}/assign", response_model=TaskInstanceResponse)
async def assign_instance(
    instance_id: int,
    data: AssignRequest,
    db: AsyncSession = Depends(get_db),
):
    instance = await db.get(TaskInstance, instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Task-Instanz nicht gefunden")

    user = await db.get(User, data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")

    instance.assigned_user_id = data.user_id
    await db.flush()

    # Task nachladen für Response
    await db.refresh(instance, ["task"])
    return instance
