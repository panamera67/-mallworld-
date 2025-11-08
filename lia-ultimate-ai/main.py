#!/usr/bin/env python3
"""
LIA ULTIMATE AI - Système Central
Orchestrateur principal de l'IA évolutive
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime

from core.twitter_connector import TwitterAPIConnector, TwitterConfig
from storage.mongodb_manager import MongoDBManager


class LIAOrchestrator:
    def __init__(self):
        self.setup_logging()
        self.running = True
        self.components = {}

    def setup_logging(self):
        """Configuration du système de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("data/logs/lia_system.log"),
                logging.StreamHandler(sys.stdout),
            ],
        )
        self.logger = logging.getLogger("LIA-Core")

    async def initialize(self):
        """Initialisation de tous les composants"""
        try:
            self.logger.info("🧠 Initialisation de LIA Ultimate AI...")

            # Configuration Twitter
            twitter_config = TwitterConfig(
                bearer_token="your_twitter_bearer_token",
                consumer_key="your_consumer_key",
                consumer_secret="your_consumer_secret",
                access_token="your_access_token",
                access_token_secret="your_access_token_secret",
            )

            self.components["twitter"] = TwitterAPIConnector(twitter_config)

            # Base de données
            self.components["database"] = MongoDBManager(
                "mongodb://localhost:27017/lia_ai"
            )

            # Test des connexions
            twitter_ok = await self.components["twitter"].initialize()
            db_ok = await self.components["database"].is_healthy()

            if twitter_ok and db_ok:
                self.logger.info("✅ Tous les composants initialisés avec succès")
                return True
            else:
                self.logger.error("❌ Échec de l'initialisation des composants")
                return False

        except Exception as e:
            self.logger.error(f"❌ Erreur critique lors de l'initialisation: {e}")
            return False

    async def start_data_collection(self):
        """Démarrage de la collecte de données"""
        self.logger.info("📥 Démarrage de la collecte de données...")

        try:
            # Démarrer le stream Twitter
            await self.components["twitter"].start_stream()

        except Exception as e:
            self.logger.error(f"❌ Erreur lors du démarrage de la collecte: {e}")

    async def shutdown(self):
        """Arrêt propre du système"""
        self.logger.info("🛑 Arrêt de LIA Ultimate AI...")
        self.running = False

        # Fermeture des connexions
        for name, component in self.components.items():
            if hasattr(component, "close"):
                await component.close()

        self.logger.info("✅ Arrêt terminé")


async def main():
    """Fonction principale"""
    global lia
    lia = LIAOrchestrator()

    def signal_handler(signum, frame):
        """Gestion des signaux d'arrêt"""
        asyncio.create_task(lia.shutdown())

    # Configuration des gestionnaires de signal
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Initialisation
    if await lia.initialize():
        # Démarrage des services
        await lia.start_data_collection()

        # Boucle principale
        while lia.running:
            await asyncio.sleep(1)

        await lia.shutdown()
    else:
        lia.logger.error("❌ Impossible de démarrer le système")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
