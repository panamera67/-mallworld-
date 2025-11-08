'use strict';

/**
 * Usage :
 *   export FIREBASE_ADMIN_SERVICE_ACCOUNT_KEY='{"type":"service_account",...}'
 *   node scripts/setAdminClaim.js add <UID>
 *   node scripts/setAdminClaim.js remove <UID>
 *   node scripts/setAdminClaim.js list
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

function ensureAppInitialized() {
  if (!admin.apps.length) {
    const serviceAccount = loadServiceAccount();
    admin.initializeApp({
      credential: admin.credential.cert(serviceAccount),
    });
  }
}

async function addAdmin(uid) {
  if (!uid) {
    throw new Error('Commande invalide. Utilisation : node scripts/setAdminClaim.js add <UID>');
  }

  ensureAppInitialized();
  const record = await admin.auth().getUser(uid);
  const claims = { ...(record.customClaims || {}), admin: true };
  await admin.auth().setCustomUserClaims(uid, claims);
  await admin.auth().revokeRefreshTokens(uid);

  console.log(`✅ Claim admin ajoutée pour ${uid} (${record.email || 'email inconnu'}).`);
  console.log("ℹ️ L'utilisateur doit se reconnecter pour appliquer la mise à jour.");
}

async function removeAdmin(uid) {
  if (!uid) {
    throw new Error('Commande invalide. Utilisation : node scripts/setAdminClaim.js remove <UID>');
  }

  ensureAppInitialized();
  const record = await admin.auth().getUser(uid);
  const claims = { ...(record.customClaims || {}) };
  delete claims.admin;
  await admin.auth().setCustomUserClaims(uid, claims);
  await admin.auth().revokeRefreshTokens(uid);

  console.log(`🗑️ Claim admin retirée pour ${uid} (${record.email || 'email inconnu'}).`);
}

async function listAdmins() {
  ensureAppInitialized();
  const admins = [];

  async function collect(nextPageToken) {
    const result = await admin.auth().listUsers(1000, nextPageToken);
    result.users.forEach((user) => {
      if (user.customClaims && user.customClaims.admin) {
        admins.push({
          uid: user.uid,
          email: user.email || 'email inconnu',
        });
      }
    });

    if (result.pageToken) {
      await collect(result.pageToken);
    }
  }

  await collect();

  if (!admins.length) {
    console.log('⚠️ Aucun utilisateur admin trouvé.');
    return;
  }

  console.log('👑 Liste des administrateurs :');
  admins.forEach((adminUser) => {
    console.log(`• ${adminUser.uid} (${adminUser.email})`);
  });
}

async function main() {
  const [, , command, uid] = process.argv;

  switch (command) {
    case 'add':
      await addAdmin(uid);
      break;
    case 'remove':
      await removeAdmin(uid);
      break;
    case 'list':
      await listAdmins();
      break;
    default:
      console.error(
        'Commande inconnue.\nUtilisation :\n  node scripts/setAdminClaim.js add <UID>\n  node scripts/setAdminClaim.js remove <UID>\n  node scripts/setAdminClaim.js list'
      );
      process.exitCode = 1;
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
