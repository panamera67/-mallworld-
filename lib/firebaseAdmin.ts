import { App, cert, getApps, initializeApp } from 'firebase-admin/app';
import { getAuth } from 'firebase-admin/auth';

let firebaseAdminApp: App | null = null;

function createAdminApp() {
  if (firebaseAdminApp) {
    return firebaseAdminApp;
  }

  const rawCredentials = process.env.FIREBASE_ADMIN_SERVICE_ACCOUNT_KEY;

  if (!rawCredentials) {
    throw new Error(
      'FIREBASE_ADMIN_SERVICE_ACCOUNT_KEY manquant. Fournissez la clé de service JSON côté serveur.'
    );
  }

  const serviceAccount = JSON.parse(rawCredentials);

  firebaseAdminApp = initializeApp({
    credential: cert(serviceAccount),
  });

  return firebaseAdminApp;
}

export function getFirebaseAdminApp() {
  if (!firebaseAdminApp) {
    if (getApps().length) {
      firebaseAdminApp = getApps()[0]!;
    } else {
      firebaseAdminApp = createAdminApp();
    }
  }

  return firebaseAdminApp;
}

export function getFirebaseAdminAuth() {
  return getAuth(getFirebaseAdminApp());
}
