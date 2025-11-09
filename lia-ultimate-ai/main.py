#!/usr/bin/env python3
"""
LIA Ultimate AI Enterprise - Point d'entrée principal.
"""

import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from core.digital_being import LIAAsDigitalBeing
from core.twitter_connector import TwitterAPIConnector
from core.youtube_connector import YouTubeConfig, YouTubeConnector
from core.reddit_connector import RedditConfig, RedditConnector
from storage.mongodb_manager import init_mongo_manager
from web.api_routes import router as api_router, set_digital_being
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
        self.background_tasks: List[asyncio.Task] = []
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

        app.include_router(api_router)
        return app

    async def initialize_components(self):
        """Initialisation des dépendances critiques."""
        self.logger.info("🚀 Initialisation LIA Enterprise Edition...")
        try:
            mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/lia_ai")
            db_manager = init_mongo_manager(mongo_uri)
            self.components["database"] = db_manager

            db_healthy = await db_manager.is_healthy()
            if not db_healthy:
                raise RuntimeError("Base de données MongoDB indisponible")

            # Twitter connector (optionnel suivant variables env)
            try:
                twitter_connector = TwitterAPIConnector.from_env()
                self.components["twitter"] = twitter_connector
                twitter_ok = await twitter_connector.initialize()
                if not twitter_ok:
                    self.logger.warning("Twitter API non initialisée complètement")
            except EnvironmentError as exc:
                self.logger.warning("Twitter désactivé (configuration incomplète): %s", exc)
            except Exception as exc:
                self.logger.error("❌ Erreur initialisation Twitter: %s", exc)

            # YouTube connector
            youtube_key = os.getenv("YOUTUBE_API_KEY")
            if youtube_key:
                youtube_connector = YouTubeConnector(YouTubeConfig(api_key=youtube_key))
                youtube_ok = await youtube_connector.initialize()
                if youtube_ok:
                    self.components["youtube"] = youtube_connector
                    task = asyncio.create_task(youtube_connector.start_monitoring())
                    self.background_tasks.append(task)
                else:
                    self.logger.warning("Connecteur YouTube non opérationnel")
            else:
                self.logger.warning("YOUTUBE_API_KEY non défini; connecteur YouTube désactivé")

            # Reddit connector
            reddit_id = os.getenv("REDDIT_CLIENT_ID")
            reddit_secret = os.getenv("REDDIT_CLIENT_SECRET")
            if reddit_id and reddit_secret:
                reddit_connector = RedditConnector(
                    RedditConfig(client_id=reddit_id, client_secret=reddit_secret)
                )
                reddit_ok = await reddit_connector.initialize()
                if reddit_ok:
                    self.components["reddit"] = reddit_connector
                    task = asyncio.create_task(reddit_connector.start_monitoring())
                    self.background_tasks.append(task)
                else:
                    self.logger.warning("Connecteur Reddit non opérationnel")
            else:
                self.logger.warning(
                    "Variables REDDIT_CLIENT_ID/REDDIT_CLIENT_SECRET absentes; connecteur Reddit désactivé"
                )

            # Digital being
            digital_config = {
                "cognitive_interval": int(os.getenv("COGNITIVE_INTERVAL", "15")),
                "importance_threshold": float(
                    os.getenv("IMPORTANCE_THRESHOLD", "0.3")
                ),
                "max_memories": int(os.getenv("MAX_MEMORIES", "10000")),
                "consciousness_growth_rate": float(
                    os.getenv("CONSCIOUSNESS_GROWTH_RATE", "0.01")
                ),
                "youtube_api_key": os.getenv("YOUTUBE_API_KEY"),
                "reddit_client_id": reddit_id,
                "reddit_client_secret": reddit_secret,
            }
            subreddit_env = os.getenv("REDDIT_SUBREDDITS")
            if subreddit_env:
                digital_config["reddit_subreddits"] = [
                    sub.strip() for sub in subreddit_env.split(",") if sub.strip()
                ]
            digital_being = LIAAsDigitalBeing(digital_config)
            set_digital_being(digital_being)
            self.components["digital_being"] = digital_being
            self.background_tasks.append(asyncio.create_task(digital_being.live()))

            self.logger.info("✅ LIA Enterprise initialisé avec succès")
        except Exception as exc:
            self.logger.error("❌ Erreur initialisation LIA Enterprise: %s", exc)
            raise

    async def shutdown_components(self):
        """Arrêt propre des composants."""
        self.logger.info("🛑 Arrêt de LIA Enterprise...")
        for task in self.background_tasks:
            task.cancel()
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
            self.background_tasks.clear()

        digital_being = self.components.get("digital_being")
        if digital_being:
            await digital_being.shutdown()

        for name, component in self.components.items():
            if name == "digital_being":
                continue
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
