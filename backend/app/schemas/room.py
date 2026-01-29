from pydantic import BaseModel


class RoomCreate(BaseModel):
    name: str
    icon: str = "mdi:room"
    point_multiplier: float = 1.0
    sort_order: int = 0
    ha_area_id: str | None = None


class RoomUpdate(BaseModel):
    name: str | None = None
    icon: str | None = None
    point_multiplier: float | None = None
    sort_order: int | None = None
    ha_area_id: str | None = None


class RoomResponse(BaseModel):
    id: int
    name: str
    icon: str
    point_multiplier: float
    sort_order: int
    ha_area_id: str | None

    model_config = {"from_attributes": True}


# --- HA Sync Schemas ---


class HaAreaInput(BaseModel):
    area_id: str
    name: str


class RoomSyncRequest(BaseModel):
    areas: list[HaAreaInput]


class RoomSyncResponse(BaseModel):
    created: list[RoomResponse]
    updated: list[RoomResponse]
    warnings: list[str]
