#!/bin/bash
# start_lia.sh

echo "🧠 LANCEMENT DE LIA ULTIMATE AI"
echo "================================"

# Vérification Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

# Création des dossiers
mkdir -p data/logs data/tweets

echo "📁 Structure créée"

# Installation des dépendances
echo "📦 Installation des dépendances..."
pip install -r requirements.txt

# Vérification des variables d'environnement
if [ ! -f ".env" ]; then
    echo "⚠️  Fichier .env non trouvé, création depuis .env.example"
    cp .env.example .env
    echo "📝 Merci de configurer vos clés API dans le fichier .env"
fi

# Démarrage des services Docker
echo "🐳 Démarrage des services Docker..."
docker-compose up -d

# Attente que MongoDB soit prêt
echo "⏳ Attente du démarrage de MongoDB..."
sleep 10

# Lancement de l'application
echo "🚀 Démarrage de LIA Core..."
python main.py

echo "✅ LIA Ultimate AI est opérationnel!"
echo "📊 Logs: tail -f data/logs/lia_system.log"
