import logging
from contextlib import asynccontextmanager
from datetime import date

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth import verify_api_key

from app.config import settings
from app.database import async_session, engine, Base
from app.routers import gamification, rooms, summaries, tasks, users
from app.seed import seed_data
from app.services.scheduler_service import start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chorequest")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Tabellen erstellen (in Produktion: Alembic nutzen)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed-Daten einfügen
    async with async_session() as db:
        await seed_data(db)

    # Task-Instanzen für heute generieren (falls noch nicht vorhanden)
    from app.services.task_service import generate_task_instances_for_date
    async with async_session() as db:
        count = await generate_task_instances_for_date(db, date.today())
        await db.commit()
        if count > 0:
            logger.info("Startup: %d Task-Instanzen für heute erstellt", count)

    # Scheduler starten
    start_scheduler()

    yield

    # Scheduler stoppen
    stop_scheduler()


app = FastAPI(
    title=settings.app_name,
    description="Gamifizierter Haushalts-Todo-Manager",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router einbinden
app.include_router(users.router)
app.include_router(rooms.router)
app.include_router(tasks.router)
app.include_router(gamification.router)
app.include_router(summaries.router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "app": settings.app_name, "version": "0.1.0"}


@app.get("/api/dashboard", dependencies=[Depends(verify_api_key)])
async def dashboard():
    """Kompakte Daten für Home Assistant Coordinator."""
    from sqlalchemy import select, func
    from sqlalchemy.orm import selectinload
    from app.models.user import User
    from app.models.room import Room
    from app.models.task import Task, TaskInstance

    async with async_session() as db:
        today = date.today()

        # Heutige offene Tasks
        tasks_today_result = await db.execute(
            select(func.count(TaskInstance.id))
            .where(TaskInstance.due_date == today)
            .where(TaskInstance.status == "pending")
        )
        tasks_today = tasks_today_result.scalar() or 0

        # Überfällige Tasks
        overdue_result = await db.execute(
            select(func.count(TaskInstance.id))
            .where(TaskInstance.due_date < today)
            .where(TaskInstance.status == "pending")
        )
        overdue = overdue_result.scalar() or 0

        # User-Punkte
        users_result = await db.execute(
            select(User).order_by(User.total_points.desc())
        )
        user_list = users_result.scalars().all()

        # Per-Room-Task-Aufschlüsselung
        rooms_result = await db.execute(select(Room).order_by(Room.sort_order, Room.name))
        rooms = rooms_result.scalars().all()

        rooms_data = []
        for room in rooms:
            # Heutige pending Tasks für diesen Raum
            room_tasks_result = await db.execute(
                select(
                    TaskInstance.id,
                    Task.title,
                    Task.base_points,
                    TaskInstance.status,
                    TaskInstance.assigned_user_id,
                )
                .join(Task, TaskInstance.task_id == Task.id)
                .where(Task.room_id == room.id)
                .where(TaskInstance.due_date == today)
                .where(TaskInstance.status == "pending")
            )
            room_tasks = [
                {
                    "instance_id": row.id,
                    "title": row.title,
                    "base_points": row.base_points,
                    "status": row.status,
                    "assigned_user_id": row.assigned_user_id,
                }
                for row in room_tasks_result.all()
            ]
            rooms_data.append({
                "room_id": room.id,
                "room_name": room.name,
                "ha_area_id": room.ha_area_id,
                "icon": room.icon,
                "tasks": room_tasks,
            })

        return {
            "tasks_today": tasks_today,
            "tasks_overdue": overdue,
            "users": [
                {
                    "id": u.id,
                    "username": u.username,
                    "display_name": u.display_name,
                    "ha_user_id": u.ha_user_id,
                    "total_points": u.total_points,
                    "weekly_points": u.weekly_points,
                    "current_streak": u.current_streak,
                }
                for u in user_list
            ],
            "rooms": rooms_data,
        }
