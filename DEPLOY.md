## MallWorld v2.3 — Deployment Checklist

### 1. Local prerequisites
- Node 18+, npm 9+ (or pnpm/yarn)
- Firebase CLI (optional, for rules deployment): `npm install -g firebase-tools`
- Vercel CLI (optional for manual deploys): `npm install -g vercel`

### 2. Install dependencies
```bash
npm install
npm install firebase firebase-admin --save
```

### 3. Configure environment variables
Create `.env.local` (already scaffolded in repo) and fill in the values:
- `NEXT_PUBLIC_API_URL`
- Supabase URL + keys
- Stripe test keys (`pk_test_*`, `sk_test_*`)
- OpenAI API key
- Firebase web config (from Firebase Console → Project settings → General → Your apps → Web)
- `SUPABASE_SERVICE_ROLE_KEY`
- `FIREBASE_ADMIN_SERVICE_ACCOUNT_KEY` (JSON string, keep **private**)

> Mirror the same variables in Vercel → Project Settings → Environment Variables (set the Firebase admin key as encrypted secret).

### 4. Firebase setup
1. Enable Authentication providers: Google + Email/Password.
2. Firestore → create collection `mall_events` with sample documents.
3. Deploy Firestore rules:
   ```bash
   firebase deploy --only firestore:rules
   ```
   (or paste the contents of `firestore.rules` into the console).

### 5. Promote an admin user
1. Create a user via Firebase Auth (sign in once through `/admin` or add manually).
2. Export your service key and grant the `admin` claim:
   ```bash
   export FIREBASE_ADMIN_SERVICE_ACCOUNT_KEY='{"type":"service_account",...}'
   node scripts/setAdminClaim.js add <USER_UID>
   ```
3. To revoke:
   ```bash
   node scripts/setAdminClaim.js remove <USER_UID>
   ```
4. List admins for verification:
   ```bash
   node scripts/setAdminClaim.js list
   ```

> L’API `/api/admin-session` vérifie le claim `admin` via l’Admin SDK puis dépose un cookie HTTP-only (`mw-admin`). Ce cookie est lu par `middleware.ts` pour protéger toutes les routes `/admin`. Assure-toi donc que la variable `FIREBASE_ADMIN_SERVICE_ACCOUNT_KEY` est bien configurée sur Vercel (production et preview).

### 6. Build & deploy (Vercel)
```bash
npx vercel build
npx vercel deploy --prod
```
Or push to GitHub and let Vercel deploy automatically.

### 7. Post-deploy checklist
- Hit `/admin`, authenticate with Google, confirm admin badge.
- CRUD events and verify Firestore updates in real time.
- Stripe webhook: add endpoint `https://mallworld-v2-3.vercel.app/api/stripe/webhook` (test mode events).
- Supabase connectivity: run health check against API endpoints using your service role if applicable.
- Inspect tes cookies : un admin connecté doit avoir `mw-admin=1` (HTTP-only). Sans ce cookie, le middleware redirigera vers `/`.

### 8. Troubleshooting tips
- **Auth claim not picked up**: user must log out/in to refresh the ID token; you can also call `getIdToken(true)` client-side.
- **Permission denied on Firestore**: confirm the admin claim, check that rules are deployed, inspect Firestore logs.
- **Vercel build failure**: ensure `firebase` package is not bundled server-side unnecessarily; Next.js 14 handles ESM automatically.
- **Stripe webhook signature**: store `STRIPE_WEBHOOK_SECRET` if you implement signature verification (add to `.env` & Vercel).
- **Redirection inattendue vers la home**: vérifie que la route `/api/admin-session` renvoie bien un statut 200 (service key valide) et que le cookie `mw-admin` est présent.

All set — your admin module is ready for production 🚀
