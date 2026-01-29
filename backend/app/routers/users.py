import logging
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import verify_api_key
from app.database import get_db
from app.models.user import User
from app.models.room import Room
from app.models.task import Task, TaskInstance
from app.models.completion import TaskCompletion, UserAchievement
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserStats,
    UserSyncRequest,
    UserSyncResponse,
    UserUpdate,
)

logger = logging.getLogger("chorequest")

router = APIRouter(prefix="/api/users", tags=["Users"], dependencies=[Depends(verify_api_key)])


@router.get("", response_model=list[UserResponse])
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).order_by(User.username))
    return result.scalars().all()


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.username == data.username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Benutzername existiert bereits")
    user = User(**data.model_dump())
    if not user.display_name:
        user.display_name = user.username.capitalize()
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@router.post("/sync", response_model=UserSyncResponse)
async def sync_users(data: UserSyncRequest, db: AsyncSession = Depends(get_db)):
    """Synchronisiert Benutzer aus Home Assistant Person-Entities."""
    created: list[User] = []
    updated: list[User] = []
    warnings: list[str] = []

    # Bestehende User mit ha_user_id laden
    result = await db.execute(select(User).where(User.ha_user_id.isnot(None)))
    existing_users = {u.ha_user_id: u for u in result.scalars().all()}

    incoming_ids = {p.person_id for p in data.persons}

    for person in data.persons:
        if person.person_id in existing_users:
            user = existing_users[person.person_id]
            if user.display_name != person.name:
                user.display_name = person.name
                updated.append(user)
                logger.info("Benutzer '%s' umbenannt (ha_user_id=%s)", person.name, person.person_id)
        else:
            # Username aus person_id ableiten (z.B. "person.lukas" → "lukas")
            username = person.person_id.replace("person.", "").replace(".", "_")
            # Prüfen ob Username schon existiert
            existing_username = await db.execute(
                select(User).where(User.username == username)
            )
            if existing_username.scalar_one_or_none():
                username = f"{username}_ha"

            user = User(
                username=username,
                display_name=person.name,
                ha_user_id=person.person_id,
            )
            db.add(user)
            created.append(user)
            logger.info("Neuer Benutzer '%s' aus HA-Person erstellt (ha_user_id=%s)", person.name, person.person_id)

    # Warnung für gelöschte Personen (kein Delete, da Punkte erhalten bleiben)
    for ha_id, user in existing_users.items():
        if ha_id not in incoming_ids:
            warnings.append(
                f"Benutzer '{user.display_name}' (ha_user_id={ha_id}) existiert nicht mehr in HA. "
                f"Benutzer bleibt erhalten (Punkte-Daten)."
            )

    await db.flush()
    for user in created + updated:
        await db.refresh(user)

    return UserSyncResponse(
        created=[UserResponse.model_validate(u) for u in created],
        updated=[UserResponse.model_validate(u) for u in updated],
        warnings=warnings,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")
    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, data: UserUpdate, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(user, key, value)
    await db.flush()
    await db.refresh(user)
    return user


@router.get("/{user_id}/stats", response_model=UserStats)
async def get_user_stats(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")

    # Gesamtanzahl Completions
    total_result = await db.execute(
        select(func.count(TaskCompletion.id)).where(TaskCompletion.user_id == user_id)
    )
    total_completed = total_result.scalar() or 0

    # Achievements
    achievements_result = await db.execute(
        select(func.count(UserAchievement.id)).where(UserAchievement.user_id == user_id)
    )
    achievements_count = achievements_result.scalar() or 0

    # Tasks diese Woche (Montag bis heute)
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    weekly_result = await db.execute(
        select(func.count(TaskCompletion.id))
        .where(TaskCompletion.user_id == user_id)
        .where(func.date(TaskCompletion.completed_at) >= week_start)
    )
    tasks_this_week = weekly_result.scalar() or 0

    # Lieblingsraum: Raum mit den meisten Completions
    favorite_room_result = await db.execute(
        select(Room.name, func.count(TaskCompletion.id).label("cnt"))
        .join(TaskInstance, TaskCompletion.task_instance_id == TaskInstance.id)
        .join(Task, TaskInstance.task_id == Task.id)
        .join(Room, Task.room_id == Room.id)
        .where(TaskCompletion.user_id == user_id)
        .group_by(Room.name)
        .order_by(func.count(TaskCompletion.id).desc())
        .limit(1)
    )
    fav_row = favorite_room_result.first()
    favorite_room = fav_row.name if fav_row else None

    return UserStats(
        user=UserResponse.model_validate(user),
        tasks_completed_total=total_completed,
        tasks_completed_this_week=tasks_this_week,
        favorite_room=favorite_room,
        achievements_count=achievements_count,
    )
