from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    room_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("rooms.id", ondelete="CASCADE")
    )
    base_points: Mapped[int] = mapped_column(Integer, default=10)
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=15)
    recurrence: Mapped[str] = mapped_column(String(20), default="once")
    recurrence_day: Mapped[int | None] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    room: Mapped["Room"] = relationship(back_populates="tasks")  # noqa: F821
    instances: Mapped[list["TaskInstance"]] = relationship(
        back_populates="task", cascade="all, delete-orphan"
    )


class TaskInstance(Base):
    __tablename__ = "task_instances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tasks.id", ondelete="CASCADE")
    )
    due_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    assigned_user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    task: Mapped["Task"] = relationship(back_populates="instances")
    assigned_user: Mapped["User | None"] = relationship(  # noqa: F821
        back_populates="assigned_instances"
    )
    completion: Mapped["TaskCompletion | None"] = relationship(  # noqa: F821
        back_populates="task_instance", uselist=False
    )
