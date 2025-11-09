#!/bin/bash

set -e

echo "🧪 TEST COMPLET DU DÉPLOIEMENT ENTERPRISE"
echo "=========================================="

BASE_URL="http://localhost:8000"
DASHBOARD_URL="http://localhost:3000"
PROMETHEUS_URL="http://localhost:9090"

if [ ! -f ".env" ]; then
    echo "❌ .env manquant"
    exit 1
fi

source .env

ADMIN_TOKEN=${JWT_ADMIN_TOKEN:-$ADMIN_JWT_TOKEN}
DASHBOARD_TOKEN=${JWT_DASHBOARD_TOKEN:-$ADMIN_TOKEN}

if [ -z "$ADMIN_TOKEN" ]; then
    echo "❌ Token admin manquant"
    exit 1
fi

test_endpoint() {
    local endpoint=$1
    local token=$2
    local expected_status=${3:-200}

    echo "→ Test $endpoint"
    response=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Authorization: Bearer $token" \
        "$BASE_URL$endpoint")

    if [ "$response" -eq "$expected_status" ]; then
        echo "✅ $endpoint - HTTP $response"
    else
        echo "❌ $endpoint - HTTP $response (attendu $expected_status)"
        exit 1
    fi
}

echo ""
echo "🏥 SANTÉ SYSTÈME"
test_endpoint "/health" "$ADMIN_TOKEN"
test_endpoint "/api/v1/health" "$ADMIN_TOKEN"

echo ""
echo "🧠 CONSCIENCE"
test_endpoint "/api/v1/consciousness/status" "$ADMIN_TOKEN"
test_endpoint "/api/v1/consciousness/metrics" "$ADMIN_TOKEN"
test_endpoint "/api/v1/consciousness/desires" "$ADMIN_TOKEN"

echo ""
echo "📊 DASHBOARD"
test_endpoint "/api/v1/dashboard/metrics" "$DASHBOARD_TOKEN"

echo ""
echo "📡 COLLECTE"
response=$(curl -s -X POST -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"platform": "twitter", "query": "AI"}' \
    "$BASE_URL/api/v1/data/collect")
echo "Réponse collecte: $response"

echo ""
echo "🐳 SERVICES DOCKER"
services=("lia-core-enterprise" "lia-dashboard" "lia-mongodb" "lia-redis" "lia-grafana" "lia-prometheus")
for service in "${services[@]}"; do
    if docker ps | grep -q "$service"; then
        echo "✅ $service en cours d'exécution"
    else
        echo "❌ $service non démarré"
    fi
done

echo ""
echo "🌐 ACCÈS DASHBOARD"
if curl -s -f "$DASHBOARD_URL" > /dev/null; then
    echo "✅ Dashboard accessible"
else
    echo "❌ Dashboard inaccessible"
fi

echo ""
echo "📈 PROMETHEUS"
if curl -s -f "$PROMETHEUS_URL/-/healthy" > /dev/null; then
    echo "✅ Prometheus healthy"
else
    echo "❌ Prometheus indisponible"
fi

echo ""
echo "🎉 Tests complétés avec succès"
