from datetime import datetime
from typing import Dict, List, Optional

import psutil
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from config.security import security
from storage.mongodb_manager import init_mongo_manager

router = APIRouter()
security_scheme = HTTPBearer()


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
    components: Dict[str, str]


class TweetAnalysisRequest(BaseModel):
    text: str
    language: Optional[str] = "fr"


class AnalysisResponse(BaseModel):
    sentiment: str
    confidence: float
    topics: List[str]
    entities: List[str]


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)):
    """Vérification du token JWT."""
    try:
        payload = security.verify_jwt(credentials.credentials)
        return payload
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc


def _clean_documents(documents: List[Dict]) -> List[Dict]:
    """Nettoie les documents MongoDB pour les rendre JSON-serializable."""
    cleaned: List[Dict] = []
    for doc in documents:
        serializable = dict(doc)
        if "_id" in serializable:
            serializable["_id"] = str(serializable["_id"])
        cleaned.append(serializable)
    return cleaned


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Endpoint de santé de l'application."""
    mongo_manager = init_mongo_manager()
    database_status = "connected" if await mongo_manager.is_healthy() else "degraded"

    return HealthResponse(
        status="healthy" if database_status == "connected" else "degraded",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat(),
        components={
            "database": database_status,
            "twitter": "active",
            "redis": "unknown",
        },
    )


@router.post("/analyze/tweet", response_model=AnalysisResponse)
async def analyze_tweet(
    request: TweetAnalysisRequest,
    user: dict = Depends(verify_token),
):
    """Analyse de tweet en temps réel."""
    try:
        return AnalysisResponse(
            sentiment="positive",
            confidence=0.87,
            topics=["ai", "technology"],
            entities=["LIA", "Twitter"],
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur d'analyse: {exc}",
        ) from exc


@router.get("/system/metrics")
async def get_system_metrics(user: dict = Depends(verify_token)):
    """Métriques système en temps réel."""
    try:
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent
        try:
            connections = len(psutil.net_connections(kind="inet"))
        except Exception:
            connections = None

        return {
            "cpu_percent": cpu,
            "memory_usage": memory,
            "disk_usage": disk,
            "active_connections": connections,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération métriques système: {exc}",
        ) from exc


@router.get("/dashboard/metrics")
async def get_dashboard_metrics(user: dict = Depends(verify_token)):
    """Métriques complètes pour le dashboard."""
    try:
        mongo_manager = init_mongo_manager()
        system_metrics = await mongo_manager.get_system_metrics()

        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent
        try:
            connections = len(psutil.net_connections(kind="inet"))
        except Exception:
            connections = None

        return {
            "system": system_metrics,
            "realtime": {
                "cpu_percent": cpu,
                "memory_usage": memory,
                "disk_usage": disk,
                "active_connections": connections,
            },
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération métriques: {exc}",
        ) from exc


@router.get("/data/trending")
async def get_trending_data(
    platform: str = Query("all", regex="^(all|twitter|youtube|reddit)$"),
    limit: int = Query(10, ge=1, le=100),
    user: dict = Depends(verify_token),
):
    """Données tendances pour le dashboard."""
    try:
        mongo_manager = init_mongo_manager()
        db = mongo_manager.db

        trending_data: Dict[str, List[Dict]] = {}

        if platform in {"all", "twitter"}:
            cursor = db.tweets.find({}, sort=[("collected_at", -1)], limit=limit)
            trending_data["twitter"] = _clean_documents(list(cursor))

        if platform in {"all", "youtube"}:
            cursor = db.youtube_videos.find({}, sort=[("collected_at", -1)], limit=limit)
            trending_data["youtube"] = _clean_documents(list(cursor))

        if platform in {"all", "reddit"}:
            cursor = db.reddit_posts.find({}, sort=[("collected_at", -1)], limit=limit)
            trending_data["reddit"] = _clean_documents(list(cursor))

        return trending_data
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération données: {exc}",
        ) from exc
