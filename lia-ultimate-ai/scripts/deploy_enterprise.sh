#!/bin/bash
# scripts/deploy_enterprise.sh

set -e

echo "🏢 LIA ULTIMATE AI - DÉPLOIEMENT ENTERPRISE"
echo "==========================================="

check_environment() {
    echo "🔍 Validation de l'environnement..."

    if ! command -v docker &> /dev/null; then
        echo "❌ Docker n'est pas installé"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose n'est pas installé"
        exit 1
    fi

    local MEM_GB
    MEM_GB=$(free -g | awk 'NR==2{print $2}')
    if [ "$MEM_GB" -lt 8 ]; then
        echo "⚠️  Mémoire insuffisante (8GB minimum recommandé)"
    fi

    echo "✅ Environnement validé"
}

build_images() {
    echo "🐳 Construction des images Docker..."
    docker-compose build --no-cache
    echo "✅ Images construites avec succès"
}

start_services() {
    echo "🚀 Démarrage des services..."

    mkdir -p data/logs data/tweets data/analytics logs
    chmod -R 755 data logs

    docker-compose up -d

    echo "⏳ Attente du démarrage des services..."
    sleep 15

    check_health
}

check_health() {
    echo "🏥 Vérification de la santé des services..."

    if curl -sf http://localhost:8000/health > /dev/null; then
        echo "✅ API principale opérationnelle"
    else
        echo "❌ API principale inaccessible"
        exit 1
    fi

    if docker exec lia-mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
        echo "✅ MongoDB opérationnel"
    else
        echo "❌ MongoDB inaccessible"
        exit 1
    fi

    echo "🎉 Tous les services sont opérationnels"
}

show_info() {
    cat <<EOF

📊 INFORMATIONS DE DÉPLOIEMENT
==============================
🌐 API principale: http://localhost:8000
📊 Dashboard: http://localhost:3000
🗄️  MongoDB: localhost:27017
🔴 Redis: localhost:6379

📚 Documentation API: http://localhost:8000/docs
🔍 Logs: docker-compose logs -f

🚀 LIA Ultimate AI Enterprise est maintenant opérationnel!
EOF
}

main() {
    check_environment
    build_images
    start_services
    show_info
}

main "$@"
