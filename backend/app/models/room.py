from sqlalchemy import Integer, String, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    icon: Mapped[str] = mapped_column(String(50), default="mdi:room")
    point_multiplier: Mapped[float] = mapped_column(Numeric(3, 2), default=1.0)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    ha_area_id: Mapped[str | None] = mapped_column(String(100), unique=True)

    tasks: Mapped[list["Task"]] = relationship(  # noqa: F821
        back_populates="room", cascade="all, delete-orphan"
    )
