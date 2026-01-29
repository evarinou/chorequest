from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import verify_api_key
from app.database import get_db
from app.models.user import User
from app.models.completion import Achievement, UserAchievement
from app.schemas.achievement import (
    AchievementProgressResponse,
    AchievementResponse,
    UserAchievementResponse,
)
from app.schemas.user import UserResponse
from app.services.achievement_service import get_achievement_progress

router = APIRouter(prefix="/api", tags=["Gamification"], dependencies=[Depends(verify_api_key)])


@router.get("/leaderboard", response_model=list[UserResponse])
async def get_leaderboard(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).order_by(User.total_points.desc()))
    return result.scalars().all()


@router.get("/leaderboard/weekly", response_model=list[UserResponse])
async def get_weekly_leaderboard(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).order_by(User.weekly_points.desc()))
    return result.scalars().all()


@router.get("/achievements", response_model=list[AchievementResponse])
async def list_achievements(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Achievement).order_by(Achievement.id))
    return result.scalars().all()


@router.get("/achievements/{user_id}", response_model=list[UserAchievementResponse])
async def get_user_achievements(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")

    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(UserAchievement)
        .options(selectinload(UserAchievement.achievement))
        .where(UserAchievement.user_id == user_id)
        .order_by(UserAchievement.unlocked_at)
    )
    return result.scalars().all()


@router.get("/achievements/{user_id}/progress", response_model=list[AchievementProgressResponse])
async def get_user_achievement_progress(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")

    progress = await get_achievement_progress(db, user)
    return [
        AchievementProgressResponse(
            achievement=AchievementResponse.model_validate(p["achievement"]),
            unlocked=p["unlocked"],
            unlocked_at=p["unlocked_at"],
            current_value=p["current_value"],
            target_value=p["target_value"],
            progress_percent=p["progress_percent"],
        )
        for p in progress
    ]
