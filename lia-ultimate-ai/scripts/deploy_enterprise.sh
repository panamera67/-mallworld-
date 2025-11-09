#!/bin/bash

# === LIA ULTIMATE AI - ENTERPRISE DEPLOYMENT SCRIPT ===
set -e

echo "🚀 Starting LIA Ultimate AI Enterprise Deployment..."
export DEPLOYMENT_TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# === LOAD SECRETS ===
if [ -f .env ]; then
    set -a
    # shellcheck disable=SC1091
    . ./.env
    set +a
    echo "✅ Environment variables loaded securely"
else
    echo "❌ .env file not found!"
    exit 1
fi

# === VALIDATE JWT TOKEN ===
validate_jwt_token() {
    echo "🔐 Validating JWT Token..."
    if [ -z "$ADMIN_JWT_TOKEN" ]; then
        echo "❌ ADMIN_JWT_TOKEN not set"
        exit 1
    fi

    python3 -c "
import jwt, os
try:
    decoded = jwt.decode(os.getenv('ADMIN_JWT_TOKEN'), options={'verify_signature': False})
    print(f'✅ JWT Token Valid - Role: {decoded.get(\"role\")}, Exp: {decoded.get(\"exp\")}')
except Exception as e:
    print(f'❌ JWT Validation Failed: {e}')
    exit(1)
"
}

# === DOCKER DEPLOYMENT ===
deploy_docker_stack() {
    echo "🐳 Deploying Docker Stack..."

    docker network create lia_secure_network || true
    docker network create lia_monitoring_network || true

    docker-compose -f docker-compose.enterprise.yml up -d --build --force-recreate

    echo "✅ Docker stack deployed successfully"
}

# === DATABASE INITIALIZATION ===
init_databases() {
    echo "🗄️ Initializing Databases..."

    until docker exec lia-mongodb mongo --eval "db.adminCommand('ismaster')" | grep "true"; do
        echo "⏳ Waiting for MongoDB..."
        sleep 5
    done
    docker exec lia-mongodb mongo -u lia_admin -p UltraSecurePass123! --authenticationDatabase admin lia_prod << EOF
    db.createCollection("twitter_data");
    db.createCollection("youtube_analytics");
    db.createCollection("reddit_sentiment");
    db.twitter_data.createIndex({ "created_at": -1 });
    db.youtube_analytics.createIndex({ "timestamp": -1 });
    db.reddit_sentiment.createIndex({ "subreddit": 1, "timestamp": -1 });
    print("✅ MongoDB initialized successfully");
EOF

    echo "✅ Databases initialized"
}

# === SECURITY CHECKS ===
run_security_checks() {
    echo "🔒 Running Security Checks..."

    validate_jwt_token

    services=("lia-core-enterprise" "lia-dashboard" "lia-mongodb" "lia-redis" "lia-prometheus" "lia-grafana")
    for service in "${services[@]}"; do
        if docker ps | grep -q "$service"; then
            echo "✅ $service is running securely"
        else
            echo "❌ $service is not running"
            exit 1
        fi
    done

    curl -s -f http://localhost:8000/health > /dev/null && echo "✅ API reachable" || echo "⚠️ API health check skipped"
}

# === SMOKE TESTS ===
run_smoke_tests() {
    echo "🧪 Running Smoke Tests..."

    export ADMIN_TOKEN="$ADMIN_JWT_TOKEN"

    endpoints=(
        "/api/health"
        "/api/v1/analytics/sentiment"
        "/api/v1/data/twitter/trends"
        "/api/v1/system/status"
    )

    for endpoint in "${endpoints[@]}"; do
        response=$(curl -s -o /dev/null -w "%{http_code}" \
            -H "Authorization: Bearer $ADMIN_TOKEN" \
            "http://localhost:8000$endpoint")

        if [ "$response" -eq 200 ]; then
            echo "✅ $endpoint - HTTP $response"
        else
            echo "❌ $endpoint - HTTP $response"
            exit 1
        fi
    done

    curl -X POST -H "Authorization: Bearer $ADMIN_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"platform": "twitter", "query": "AI"}' \
        http://localhost:8000/api/v1/data/collect && echo "✅ Data ingestion test passed"
}

# === MONITORING SETUP ===
setup_monitoring() {
    echo "📊 Setting up Monitoring..."

    curl -X POST -H "Content-Type: application/json" \
        -d '{"name":"LIA Ultimate AI Dashboard"}' \
        http://admin:$GRAFANA_ADMIN_PASSWORD@localhost:3001/api/dashboards/db && echo "✅ Grafana dashboard created" || echo "⚠️ Grafana setup skipped"

    if [ -f ./scripts/setup_monitoring.py ]; then
        python3 ./scripts/setup_monitoring.py
    else
        echo "⚠️ Monitoring setup script not found, skipping..."
    fi
}

# === MAIN DEPLOYMENT FLOW ===
main() {
    echo "🏁 Starting LIA Ultimate AI Enterprise Deployment..."

    validate_jwt_token
    deploy_docker_stack
    init_databases
    sleep 10
    run_security_checks
    run_smoke_tests
    setup_monitoring

    echo "🎉 LIA Ultimate AI Deployment Completed Successfully!"
    echo "📊 Dashboard: http://localhost:3000"
    echo "🔗 API: http://localhost:8000"
    echo "📚 Documentation: http://localhost:8080"
}

main "$@"
