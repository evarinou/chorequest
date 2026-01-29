from datetime import date, datetime

from sqlalchemy import JSON, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TaskCompletion(Base):
    __tablename__ = "task_completions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_instance_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("task_instances.id", ondelete="CASCADE")
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE")
    )
    completed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    points_earned: Mapped[int] = mapped_column(Integer, nullable=False)
    bonus_points: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str | None] = mapped_column(Text)

    task_instance: Mapped["TaskInstance"] = relationship(  # noqa: F821
        back_populates="completion"
    )
    user: Mapped["User"] = relationship(back_populates="completions")  # noqa: F821


class Achievement(Base):
    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    icon: Mapped[str | None] = mapped_column(String(50))
    criteria: Mapped[dict] = mapped_column(JSON, nullable=False)
    points_reward: Mapped[int] = mapped_column(Integer, default=50)

    user_achievements: Mapped[list["UserAchievement"]] = relationship(
        back_populates="achievement", cascade="all, delete-orphan"
    )


class UserAchievement(Base):
    __tablename__ = "user_achievements"
    __table_args__ = (UniqueConstraint("user_id", "achievement_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE")
    )
    achievement_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("achievements.id", ondelete="CASCADE")
    )
    unlocked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="achievements")  # noqa: F821
    achievement: Mapped["Achievement"] = relationship(
        back_populates="user_achievements"
    )


class WeeklySummary(Base):
    __tablename__ = "weekly_summaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    week_start: Mapped[date] = mapped_column(Date, nullable=False)
    week_end: Mapped[date] = mapped_column(Date, nullable=False)
    summary_text: Mapped[str | None] = mapped_column(Text)
    suggested_tasks: Mapped[dict | None] = mapped_column(JSON)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
