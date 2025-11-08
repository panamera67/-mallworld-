'use strict';

/**
 * Usage:
 *   export FIREBASE_ADMIN_SERVICE_ACCOUNT_KEY='{"type":"service_account",...}'
 *   node scripts/setAdminClaim.js <USER_UID>
 */

const admin = require('firebase-admin');

function loadServiceAccount() {
  const rawKey = process.env.FIREBASE_ADMIN_SERVICE_ACCOUNT_KEY;

  if (!rawKey) {
    throw new Error(
      'FIREBASE_ADMIN_SERVICE_ACCOUNT_KEY manquant. Fournissez la clé de service JSON stringifiée.'
    );
  }

  try {
    return JSON.parse(rawKey);
  } catch (error) {
    throw new Error(
      'Impossible de parser FIREBASE_ADMIN_SERVICE_ACCOUNT_KEY. Vérifiez que la valeur est une chaîne JSON valide.'
    );
  }
}

async function setAdminClaim(uid) {
  if (!uid) {
    throw new Error('Veuillez fournir un UID Firebase en argument.');
  }

  const serviceAccount = loadServiceAccount();

  admin.initializeApp({
    credential: admin.credential.cert(serviceAccount),
  });

  await admin.auth().setCustomUserClaims(uid, { admin: true });
  await admin.auth().revokeRefreshTokens(uid);

  console.log(`Le rôle admin a été attribué à l'utilisateur ${uid}.`);
  console.log(
    'Demandez à l’utilisateur de se reconnecter pour rafraîchir ses droits.'
  );
}

const [, , uid] = process.argv;

setAdminClaim(uid).catch((error) => {
  console.error(error);
  process.exit(1);
});
