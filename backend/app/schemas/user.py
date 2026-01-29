from datetime import datetime

from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    display_name: str | None = None
    avatar_url: str | None = None
    ha_user_id: str | None = None


class UserUpdate(BaseModel):
    display_name: str | None = None
    avatar_url: str | None = None


class UserResponse(BaseModel):
    id: int
    username: str
    display_name: str | None
    avatar_url: str | None
    total_points: int
    weekly_points: int
    current_streak: int
    longest_streak: int
    ha_user_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserStats(BaseModel):
    user: UserResponse
    tasks_completed_total: int
    tasks_completed_this_week: int
    favorite_room: str | None
    achievements_count: int


# --- HA Sync Schemas ---


class HaPersonInput(BaseModel):
    person_id: str
    name: str


class UserSyncRequest(BaseModel):
    persons: list[HaPersonInput]


class UserSyncResponse(BaseModel):
    created: list[UserResponse]
    updated: list[UserResponse]
    warnings: list[str]
