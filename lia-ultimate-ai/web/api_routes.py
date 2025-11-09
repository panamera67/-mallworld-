import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from config.security import get_current_user, security_manager
from core.digital_being import LIAAsDigitalBeing
from core.prometheus_metrics import (
    API_REQUESTS,
    REQUEST_DURATION,
    CONTENT_TYPE_LATEST,
    generate_latest,
    update_consciousness_metrics,
)
from storage.mongodb_manager import init_mongo_manager

router = APIRouter()
logger = logging.getLogger("API")

lia_being: Optional[LIAAsDigitalBeing] = None


def set_digital_being(instance: LIAAsDigitalBeing) -> None:
    global lia_being
    lia_being = instance


def _record_request(endpoint: str, method: str, start_time: float) -> None:
    duration = time.perf_counter() - start_time
    try:
        API_REQUESTS.labels(endpoint=endpoint, method=method).inc()
    except Exception:
        logger.debug("Unable to record API_REQUESTS metric", exc_info=True)
    try:
        REQUEST_DURATION.observe(duration)
    except Exception:
        logger.debug("Unable to record REQUEST_DURATION metric", exc_info=True)


def _get_timestamp() -> float:
    try:
        return asyncio.get_running_loop().time()
    except RuntimeError:
        return time.time()


def _ensure_being() -> LIAAsDigitalBeing:
    if lia_being is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Digital Being non initialisé",
        )
    return lia_being


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    start = time.perf_counter()
    try:
        mongo = init_mongo_manager()
        try:
            database_status = (
                "connected" if await mongo.is_healthy() else "degraded"
            )
        except Exception:
            database_status = "unknown"

        status_value = (
            "healthy" if database_status == "connected" else "degraded"
        )
        return {
            "status": status_value,
            "service": "LIA Ultimate AI",
            "components": {
                "database": database_status,
                "cache": "unknown",
            },
            "timestamp": _get_timestamp(),
        }
    finally:
        _record_request("/health", "GET", start)


@router.get("/api/v1/health")
async def api_health_check(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    start = time.perf_counter()
    try:
        mongo = init_mongo_manager()
        db_status = "connected" if await mongo.is_healthy() else "degraded"
        being = lia_being
        consciousness_status = (
            "active" if being and being.awake else "inactive"
        )
        return {
            "status": "operational",
            "version": "1.0.0",
            "components": {
                "api": "healthy",
                "database": db_status,
                "cache": "unknown",
                "consciousness": consciousness_status,
            },
            "timestamp": _get_timestamp(),
        }
    finally:
        _record_request("/api/v1/health", "GET", start)


@router.get("/api/v1/consciousness/status")
async def get_consciousness_status(
    current_user: Dict[str, Any] = Depends(get_current_user),
    digital_being: LIAAsDigitalBeing = Depends(_ensure_being),
) -> Dict[str, Any]:
    start = time.perf_counter()
    try:
        status_payload = digital_being.get_status()
        update_consciousness_metrics(digital_being)
        return {
            "success": True,
            "data": status_payload,
            "timestamp": _get_timestamp(),
        }
    finally:
        _record_request("/api/v1/consciousness/status", "GET", start)


@router.get("/api/v1/consciousness/metrics")
async def get_consciousness_metrics(
    current_user: Dict[str, Any] = Depends(get_current_user),
    digital_being: LIAAsDigitalBeing = Depends(_ensure_being),
) -> Dict[str, Any]:
    start = time.perf_counter()
    try:
        status_payload = digital_being.get_status()
        metrics = {
            "consciousness_level": status_payload["consciousness_level"],
            "internal_state": status_payload["internal_state"],
            "active_desires_count": len(status_payload["active_desires"]),
            "personality_traits": status_payload["personality_traits"],
            "world_model_complexity": status_payload["world_model_complexity"],
            "uptime_seconds": status_payload["uptime_seconds"],
            "awake": status_payload["awake"],
        }
        update_consciousness_metrics(digital_being)
        return {
            "success": True,
            "metrics": metrics,
            "timestamp": _get_timestamp(),
        }
    finally:
        _record_request("/api/v1/consciousness/metrics", "GET", start)


@router.get("/api/v1/consciousness/memories")
async def get_recent_memories(
    limit: int = 10,
    current_user: Dict[str, Any] = Depends(get_current_user),
    digital_being: LIAAsDigitalBeing = Depends(_ensure_being),
) -> Dict[str, Any]:
    start = time.perf_counter()
    try:
        timeline = digital_being.memory.timeline[-limit:]
        memories: List[Dict[str, Any]] = []
        for fragment_id in reversed(timeline):
            fragment = digital_being.memory.fragments.get(fragment_id)
            if not fragment:
                continue
            memories.append(
                {
                    "id": str(fragment.id),
                    "type": fragment.type,
                    "content": fragment.content,
                    "importance": fragment.importance,
                    "emotional_valence": fragment.emotional_valence,
                    "timestamp": fragment.timestamp.isoformat(),
                }
            )

        return {
            "success": True,
            "memories": memories,
            "count": len(memories),
            "limit": limit,
        }
    finally:
        _record_request("/api/v1/consciousness/memories", "GET", start)


@router.get("/api/v1/consciousness/desires")
async def get_active_desires(
    current_user: Dict[str, Any] = Depends(get_current_user),
    digital_being: LIAAsDigitalBeing = Depends(_ensure_being),
) -> Dict[str, Any]:
    start = time.perf_counter()
    try:
        desires = digital_being.desires.get_active_desires()
        return {
            "success": True,
            "desires": desires,
            "count": len(desires),
            "timestamp": _get_timestamp(),
        }
    finally:
        _record_request("/api/v1/consciousness/desires", "GET", start)


@router.post("/api/v1/data/collect")
async def trigger_data_collection(
    payload: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    start = time.perf_counter()
    try:
        platform = payload.get("platform", "twitter")
        query = payload.get("query", "")
        logger.info("Collecte déclenchée: %s / %s", platform, query)
        return {
            "success": True,
            "message": f"Collecte {platform} démarrée",
            "query": query,
            "platform": platform,
        }
    finally:
        _record_request("/api/v1/data/collect", "POST", start)


@router.get("/api/v1/dashboard/metrics")
async def get_dashboard_metrics(
    current_user: Dict[str, Any] = Depends(get_current_user),
    digital_being: LIAAsDigitalBeing = Depends(_ensure_being),
) -> Dict[str, Any]:
    start = time.perf_counter()
    try:
        status_payload = digital_being.get_status()
        response = {
            "success": True,
            "dashboard": {
                "consciousness": {
                    "level": status_payload["consciousness_level"],
                    "awake": status_payload["awake"],
                    "phase": lia_being.awakening.current_phase if lia_being else "unknown",
                },
                "cognitive_state": status_payload["internal_state"],
                "desires": {
                    "active": len(status_payload["active_desires"]),
                    "types": [d["type"] for d in status_payload["active_desires"]],
                },
                "personality": status_payload["personality_traits"],
                "system": {
                    "uptime": status_payload["uptime_seconds"],
                    "health": "optimal",
                },
            },
        }
        return response
    finally:
        _record_request("/api/v1/dashboard/metrics", "GET", start)


@router.get("/api/generate-token")
async def generate_dashboard_token() -> Dict[str, Any]:
    start = time.perf_counter()
    try:
        token = security_manager.create_jwt(
            {
                "user_id": "dashboard-viewer",
                "username": "dashboard",
                "role": "viewer",
                "permissions": ["read"],
            },
            expires_hours=24,
        )
        return {"token": token}
    finally:
        _record_request("/api/generate-token", "GET", start)


@router.get("/metrics")
async def prometheus_metrics_endpoint() -> Response:
    start = time.perf_counter()
    try:
        payload = generate_latest()
        return Response(payload, media_type=CONTENT_TYPE_LATEST)
    finally:
        _record_request("/metrics", "GET", start)


@router.get("/api/v1/data/trending")
async def get_trending_data(
    platform: str = Query("all", regex="^(all|twitter|youtube|reddit)$"),
    limit: int = Query(10, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    start = time.perf_counter()
    try:
        mongo = init_mongo_manager()
        db = mongo.db
        trending: Dict[str, List[Dict[str, Any]]] = {}

        if platform in {"all", "twitter"} and db:
            cursor = db.tweets.find({}, sort=[("collected_at", -1)], limit=limit)
            trending["twitter"] = _clean_documents(list(cursor))
        if platform in {"all", "youtube"} and db:
            cursor = db.youtube_videos.find({}, sort=[("collected_at", -1)], limit=limit)
            trending["youtube"] = _clean_documents(list(cursor))
        if platform in {"all", "reddit"} and db:
            cursor = db.reddit_posts.find({}, sort=[("collected_at", -1)], limit=limit)
            trending["reddit"] = _clean_documents(list(cursor))

        return {"success": True, "data": trending}
    finally:
        _record_request("/api/v1/data/trending", "GET", start)


def _clean_documents(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    cleaned: List[Dict[str, Any]] = []
    for doc in documents:
        serializable = dict(doc)
        if "_id" in serializable:
            serializable["_id"] = str(serializable["_id"])
        cleaned.append(serializable)
    return cleaned


__all__ = ["router", "set_digital_being"]
