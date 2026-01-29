from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import verify_api_key
from app.database import get_db
from app.models.completion import WeeklySummary
from app.schemas.summary import (
    GenerateSummaryRequest,
    GenerateSummaryResponse,
    WeeklySummaryResponse,
)
from app.services.claude_service import generate_weekly_summary

router = APIRouter(
    prefix="/api/summaries",
    tags=["Zusammenfassungen"],
    dependencies=[Depends(verify_api_key)],
)


@router.get("", response_model=list[WeeklySummaryResponse])
async def list_summaries(
    limit: int = Query(default=10, ge=1, le=52),
    db: AsyncSession = Depends(get_db),
):
    """Alle Wochen-Zusammenfassungen (neueste zuerst)."""
    result = await db.execute(
        select(WeeklySummary)
        .order_by(WeeklySummary.week_start.desc())
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/latest", response_model=WeeklySummaryResponse)
async def get_latest_summary(db: AsyncSession = Depends(get_db)):
    """Neueste Wochen-Zusammenfassung."""
    result = await db.execute(
        select(WeeklySummary).order_by(WeeklySummary.week_start.desc()).limit(1)
    )
    summary = result.scalar_one_or_none()
    if not summary:
        raise HTTPException(status_code=404, detail="Noch keine Zusammenfassung vorhanden")
    return summary


@router.post("/generate", response_model=GenerateSummaryResponse)
async def generate_summary(
    body: GenerateSummaryRequest | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Wochen-Zusammenfassung manuell generieren."""
    week_start = body.week_start if body else None
    summary, tokens_used = await generate_weekly_summary(db, week_start)
    return GenerateSummaryResponse(
        summary=WeeklySummaryResponse.model_validate(summary),
        tokens_used=tokens_used,
    )
