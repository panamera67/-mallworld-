# Spectra FX Platform

Landing page autonome + backend ROI API + infrastructure DevOps prête pour la production.

## Structure

- `index.html` – landing page responsive, accessible (WCAG 2.1 AA) avec calculateur ROI.
- `backend/` – API Node.js/TypeScript (Express + Zod + Pino).
- `infra/` – assets d'infrastructure (Docker, Nginx, manifestes Kubernetes).
- `docker-compose.yml` – stack locale (frontend + API).

## Démarrage rapide

```bash
# 1. Backend API
cd backend
cp .env.example .env
npm install
npm run dev

# 2. Frontend statique
open ../index.html # ou servez via docker-compose (cf. infra)
```

## Tests & Qualité

```bash
cd backend
npm run lint
npm test
```

La suite Jest produit un rapport de couverture (LCOV/Cobertura) exploitable par la CI.

## Containerisation

```bash
# Images production prêtes :
docker build -t spectra-fx/api:latest -f backend/Dockerfile backend
docker build -t spectra-fx/frontend:latest -f infra/frontend/Dockerfile .

# Stack locale
docker compose up --build
# Front : http://localhost:8081 / API : http://localhost:8080
```

## CI/CD

Un workflow GitHub Actions (`.github/workflows/ci.yml`) exécute :

1. Lint + tests backend (Node 18, npm ci, couverture uploadée).
2. Build des images Docker backend & frontend via Buildx (sans push).

## Kubernetes (Helm-ready)

`infra/k8s` contient des manifestes de base :

- `backend.yaml` : namespace, ConfigMap, Deployment (2 replicas), Service.
- `frontend.yaml` : Deployment (2 replicas), Service, Ingress (routing /api → backend).

> Remplacez les images `ghcr.io/example/...` par vos registres. Les probes HTTP ciblent `/health` et `/healthz`.

## Sécurité & Observabilité

- Headers de sécurité activés (Helmet côté API, Nginx côté frontend).
- Validation stricte via Zod (toutes les entrées utilisateur).
- Logs structurés JSON (Pino) + version prettifiée en dev.
- Health checks exposés (`/health`, `/healthz`) pour monitoring et orchestrateurs.
