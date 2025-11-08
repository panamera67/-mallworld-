## Spectra FX Backend API

API Node.js/TypeScript fournissant les capacités server-side pour la landing page Spectra FX.

### Pré requis

- Node.js 18.18+ / npm 9+

### Installation

```bash
npm install
cp .env.example .env
```

### Commandes disponibles

- `npm run dev` : démarre l'API en mode développement avec rechargement à chaud.
- `npm run build` : compile le projet TypeScript dans `dist/`.
- `npm start` : lance l'API à partir des fichiers compilés.
- `npm test` : exécute la suite de tests Jest (couverture générée dans `coverage/`).
- `npm run lint` : analyse statique via ESLint.

### Endpoints

- `GET /health` : état du service (monitoring / liveness probe).
- `POST /api/v1/roi` : calcule les économies (payload : `volume`, `spread`, `optimization`).
- `POST /api/v1/contact` : enregistre une demande de contact commerciale.

Les schémas de validation et règles de conformité RGPD sont gérés avec `zod`. Les logs sont produits avec `pino` (JSON) et `pino-pretty` en local pour la lisibilité.

### Tests & Qualité

```bash
npm test
npm run lint
```

Les tests couvrent les cas nominaux et les validations d'entrée. La configuration Jest génère également `lcov` et `cobertura` pour intégration CI/CD.
