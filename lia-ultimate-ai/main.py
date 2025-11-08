#!/usr/bin/env python3
"""
LIA Ultimate AI Enterprise - Point d'entrée principal.
"""

import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from core.twitter_connector import TwitterAPIConnector
from storage.mongodb_manager import MongoDBManager
from web.api_routes import router as api_router
from config.security import security  # noqa: F401  # Force initialisation sécurité


class CorrelationIdFilter(logging.Filter):
    """Ajoute un identifiant de corrélation par défaut au contexte de log."""

    def filter(self, record: logging.LogRecord) -> bool:  # type: ignore[override]
        if not hasattr(record, "correlation_id"):
            record.correlation_id = "system"
        return True


class LIAEnterpriseOrchestrator:
    def __init__(self):
        self.components = {}
        self._ensure_directories()
        self._setup_logging()
        self.app = self._create_fastapi_app()

    def _ensure_directories(self):
        Path("logs").mkdir(parents=True, exist_ok=True)
        Path("data").mkdir(parents=True, exist_ok=True)

    def _setup_logging(self):
        """Configuration du logging enterprise avec corrélation."""
        logging.basicConfig(
            level=os.getenv("LOG_LEVEL", "INFO"),
            format="%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] - %(message)s",
            handlers=[
                logging.FileHandler("logs/lia_enterprise.log"),
                logging.StreamHandler(sys.stdout),
            ],
        )
        for handler in logging.getLogger().handlers:
            handler.addFilter(CorrelationIdFilter())
        self.logger = logging.getLogger("LIA-Enterprise")

    def _create_fastapi_app(self) -> FastAPI:
        """Initialise l'application FastAPI avec cycle de vie."""

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            await self.initialize_components()
            yield
            await self.shutdown_components()

        app = FastAPI(
            title="LIA Ultimate AI Enterprise",
            description="Intelligence Artificielle Évolutive de Niveau Entreprise",
            version="1.0.0",
            lifespan=lifespan,
        )

        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @app.get("/health")
        async def root_health():
            return {"status": "healthy", "version": "1.0.0"}

        app.include_router(api_router, prefix="/api/v1")
        return app

    async def initialize_components(self):
        """Initialisation des dépendances critiques."""
        self.logger.info("🚀 Initialisation LIA Enterprise Edition...")
        try:
            mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/lia_ai")
            self.components["database"] = MongoDBManager(connection_string=mongo_uri)

            self.components["twitter"] = TwitterAPIConnector.from_env()

            db_healthy = await self.components["database"].is_healthy()
            twitter_ok = await self.components["twitter"].initialize()

            if not db_healthy:
                raise RuntimeError("Base de données MongoDB indisponible")
            if not twitter_ok:
                self.logger.warning("Twitter API non initialisée complètement")

            self.logger.info("✅ LIA Enterprise initialisé avec succès")
        except Exception as exc:
            self.logger.error("❌ Erreur initialisation LIA Enterprise: %s", exc)
            raise

    async def shutdown_components(self):
        """Arrêt propre des composants."""
        self.logger.info("🛑 Arrêt de LIA Enterprise...")
        for component in self.components.values():
            if hasattr(component, "close"):
                await component.close()
        self.logger.info("✅ Arrêt terminé")


lia_system = LIAEnterpriseOrchestrator()
app = lia_system.app

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("ENVIRONMENT", "development") == "development",
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
    )
