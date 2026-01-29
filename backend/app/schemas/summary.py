from datetime import date, datetime

from pydantic import BaseModel


class SuggestedTask(BaseModel):
    title: str
    description: str
    room_name: str
    estimated_minutes: int
    reason: str


class WeeklySummaryResponse(BaseModel):
    id: int
    week_start: date
    week_end: date
    summary_text: str | None
    suggested_tasks: list[SuggestedTask] | None = None
    generated_at: datetime

    model_config = {"from_attributes": True}


class GenerateSummaryRequest(BaseModel):
    week_start: date | None = None


class GenerateSummaryResponse(BaseModel):
    summary: WeeklySummaryResponse
    tokens_used: int
