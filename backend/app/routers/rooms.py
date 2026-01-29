import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import verify_api_key
from app.database import get_db
from app.models.room import Room
from app.schemas.room import (
    RoomCreate,
    RoomResponse,
    RoomSyncRequest,
    RoomSyncResponse,
    RoomUpdate,
)

logger = logging.getLogger("chorequest")

router = APIRouter(prefix="/api/rooms", tags=["Rooms"], dependencies=[Depends(verify_api_key)])

# Icon-Mapping: HA-Area-Name (lowercase) → Material Design Icon
AREA_ICON_MAP: dict[str, str] = {
    "küche": "mdi:silverware-fork-knife",
    "kueche": "mdi:silverware-fork-knife",
    "kitchen": "mdi:silverware-fork-knife",
    "bad": "mdi:shower",
    "badezimmer": "mdi:shower",
    "bathroom": "mdi:shower",
    "wohnzimmer": "mdi:sofa",
    "living_room": "mdi:sofa",
    "schlafzimmer": "mdi:bed",
    "bedroom": "mdi:bed",
    "kinderzimmer": "mdi:baby-face-outline",
    "arbeitszimmer": "mdi:desk",
    "büro": "mdi:desk",
    "buero": "mdi:desk",
    "office": "mdi:desk",
    "flur": "mdi:door-open",
    "eingang": "mdi:door-open",
    "hallway": "mdi:door-open",
    "garage": "mdi:garage",
    "keller": "mdi:stairs-down",
    "basement": "mdi:stairs-down",
    "garten": "mdi:flower",
    "garden": "mdi:flower",
    "balkon": "mdi:balcony",
    "balcony": "mdi:balcony",
    "terrasse": "mdi:terrace",
    "terrace": "mdi:terrace",
    "waschküche": "mdi:washing-machine",
    "laundry": "mdi:washing-machine",
    "esszimmer": "mdi:table-furniture",
    "dining_room": "mdi:table-furniture",
    "dachboden": "mdi:home-roof",
    "attic": "mdi:home-roof",
    "toilette": "mdi:toilet",
    "wc": "mdi:toilet",
    "gäste-wc": "mdi:toilet",
}


def _icon_for_area(area_name: str) -> str:
    """Versuche ein passendes Icon anhand des Area-Namens zu finden."""
    key = area_name.lower().strip()
    return AREA_ICON_MAP.get(key, "mdi:room")


@router.get("", response_model=list[RoomResponse])
async def list_rooms(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Room).order_by(Room.sort_order, Room.name))
    return result.scalars().all()


@router.post("", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(data: RoomCreate, db: AsyncSession = Depends(get_db)):
    room = Room(**data.model_dump())
    db.add(room)
    await db.flush()
    await db.refresh(room)
    return room


@router.post("/sync", response_model=RoomSyncResponse)
async def sync_rooms(data: RoomSyncRequest, db: AsyncSession = Depends(get_db)):
    """Synchronisiert Räume aus Home Assistant Areas."""
    created: list[Room] = []
    updated: list[Room] = []
    warnings: list[str] = []

    # Bestehende Räume mit ha_area_id laden
    result = await db.execute(select(Room).where(Room.ha_area_id.isnot(None)))
    existing_rooms = {r.ha_area_id: r for r in result.scalars().all()}

    incoming_ids = {a.area_id for a in data.areas}

    for area in data.areas:
        if area.area_id in existing_rooms:
            room = existing_rooms[area.area_id]
            if room.name != area.name:
                room.name = area.name
                updated.append(room)
                logger.info("Raum '%s' umbenannt (ha_area_id=%s)", area.name, area.area_id)
        else:
            room = Room(
                name=area.name,
                ha_area_id=area.area_id,
                icon=_icon_for_area(area.name),
            )
            db.add(room)
            created.append(room)
            logger.info("Neuer Raum '%s' aus HA-Area erstellt (ha_area_id=%s)", area.name, area.area_id)

    # Warnung für gelöschte Areas (kein automatisches Löschen)
    for ha_id, room in existing_rooms.items():
        if ha_id not in incoming_ids:
            warnings.append(
                f"Raum '{room.name}' (ha_area_id={ha_id}) existiert nicht mehr in HA. "
                f"Manuelles Löschen erforderlich."
            )

    await db.flush()
    for room in created + updated:
        await db.refresh(room)

    return RoomSyncResponse(
        created=[RoomResponse.model_validate(r) for r in created],
        updated=[RoomResponse.model_validate(r) for r in updated],
        warnings=warnings,
    )


@router.patch("/{room_id}", response_model=RoomResponse)
async def update_room(room_id: int, data: RoomUpdate, db: AsyncSession = Depends(get_db)):
    room = await db.get(Room, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Raum nicht gefunden")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(room, key, value)
    await db.flush()
    await db.refresh(room)
    return room


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(room_id: int, db: AsyncSession = Depends(get_db)):
    room = await db.get(Room, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Raum nicht gefunden")
    await db.delete(room)
