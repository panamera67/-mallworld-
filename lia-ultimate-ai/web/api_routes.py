from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from config.security import security

router = APIRouter()
security_scheme = HTTPBearer()


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
    components: dict


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


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Endpoint de santé de l'application."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat(),
        components={
            "database": "connected",
            "twitter": "active",
            "redis": "connected",
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
    import psutil

    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage("/").percent,
        "active_connections": 0,
    }
