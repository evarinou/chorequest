from datetime import datetime

from pydantic import BaseModel


class AchievementResponse(BaseModel):
    id: int
    name: str
    description: str | None
    icon: str | None
    criteria: dict
    points_reward: int

    model_config = {"from_attributes": True}


class UserAchievementResponse(BaseModel):
    id: int
    user_id: int
    achievement_id: int
    unlocked_at: datetime
    achievement: AchievementResponse

    model_config = {"from_attributes": True}


class AchievementProgressResponse(BaseModel):
    achievement: AchievementResponse
    unlocked: bool
    unlocked_at: datetime | None = None
    current_value: int
    target_value: int
    progress_percent: float
