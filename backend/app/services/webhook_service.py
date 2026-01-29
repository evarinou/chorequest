"""Webhook-Service: Benachrichtigt Home Assistant über Events."""

import asyncio
import logging

import httpx

from app.config import settings

logger = logging.getLogger("chorequest.webhook")


async def _send_webhook(event_type: str, data: dict) -> None:
    """Sendet einen Webhook an Home Assistant (fire-and-forget)."""
    if not settings.ha_url or not settings.ha_webhook_id:
        return

    url = f"{settings.ha_url}/api/webhook/{settings.ha_webhook_id}"
    payload = {"event_type": event_type, **data}

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(url, json=payload)
            logger.debug("Webhook gesendet: %s -> %d", event_type, resp.status_code)
    except Exception as e:
        logger.warning("Webhook fehlgeschlagen (%s): %s", event_type, e)


def notify_task_completed(
    instance_id: int,
    task_title: str,
    user_name: str,
    points: int,
    room_name: str,
) -> None:
    """Benachrichtigt HA über eine erledigte Aufgabe (fire-and-forget)."""
    asyncio.create_task(
        _send_webhook(
            "task_completed",
            {
                "instance_id": instance_id,
                "task_title": task_title,
                "user_name": user_name,
                "points": points,
                "room_name": room_name,
            },
        )
    )


def notify_achievement_unlocked(
    user_name: str,
    achievement_name: str,
    icon: str | None,
    points_reward: int,
) -> None:
    """Benachrichtigt HA über ein freigeschaltetes Achievement (fire-and-forget)."""
    asyncio.create_task(
        _send_webhook(
            "achievement_unlocked",
            {
                "user_name": user_name,
                "achievement_name": achievement_name,
                "icon": icon or "mdi:trophy",
                "points_reward": points_reward,
            },
        )
    )
