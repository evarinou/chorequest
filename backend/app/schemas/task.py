from datetime import date, datetime

from pydantic import BaseModel

from app.schemas.room import RoomResponse
from app.schemas.user import UserResponse


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    room_id: int
    base_points: int = 10
    estimated_minutes: int = 15
    recurrence: str = "once"
    recurrence_day: int | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    room_id: int | None = None
    base_points: int | None = None
    estimated_minutes: int | None = None
    recurrence: str | None = None
    recurrence_day: int | None = None
    is_active: bool | None = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    room_id: int
    base_points: int
    estimated_minutes: int
    recurrence: str
    recurrence_day: int | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TaskWithRoom(TaskResponse):
    room: RoomResponse


class TaskInstanceResponse(BaseModel):
    id: int
    task_id: int
    due_date: date | None
    status: str
    assigned_user_id: int | None
    created_at: datetime
    task: TaskResponse

    model_config = {"from_attributes": True}


class TaskInstanceWithDetails(TaskInstanceResponse):
    assigned_user: UserResponse | None = None


class CompleteRequest(BaseModel):
    user_id: int
    notes: str | None = None


class AssignRequest(BaseModel):
    user_id: int


class CompletionResponse(BaseModel):
    id: int
    task_instance_id: int
    user_id: int
    completed_at: datetime
    points_earned: int
    bonus_points: int
    notes: str | None

    model_config = {"from_attributes": True}


class BonusBreakdown(BaseModel):
    base_points: int
    room_multiplier: float
    early_bonus: float
    streak_bonus: float
    room_completion_bonus: float
    total_points: int
    bonus_points: int


class StreakUpdate(BaseModel):
    current_streak: int
    longest_streak: int
    streak_bonus_active: bool


class UnlockedAchievement(BaseModel):
    id: int
    name: str
    description: str | None
    icon: str | None
    points_reward: int


class ExtendedCompletionResponse(BaseModel):
    completion: CompletionResponse
    bonus_breakdown: BonusBreakdown
    streak: StreakUpdate
    unlocked_achievements: list[UnlockedAchievement]
