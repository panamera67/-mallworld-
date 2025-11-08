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

async function addAdmin(uid, options = {}) {
  if (!uid) {
    throw new Error(
      'Commande invalide. Utilisation : node scripts/setAdminClaim.js add <UID> [--roles=role1,role2] [--permissions=perm1,perm2]'
    );
  }

  ensureAppInitialized();
  const record = await admin.auth().getUser(uid);
  const claims = { ...(record.customClaims || {}), admin: true };

  if (options.roles) {
    claims.roles = options.roles;
  }

  if (options.permissions) {
    claims.permissions = options.permissions;
  }

  await admin.auth().setCustomUserClaims(uid, claims);
  await admin.auth().revokeRefreshTokens(uid);

  console.log(
    `✅ Claim admin ajoutée pour ${uid} (${record.email || 'email inconnu'}).`
  );
  if (options.roles) {
    console.log(`   • Rôles assignés : ${options.roles.join(', ')}`);
  }
  if (options.permissions) {
    console.log(`   • Permissions assignées : ${options.permissions.join(', ')}`);
  }
  console.log(
    "ℹ️ L'utilisateur doit se reconnecter pour appliquer la mise à jour."
  );
}

async function removeAdmin(uid) {
  if (!uid) {
    throw new Error('Commande invalide. Utilisation : node scripts/setAdminClaim.js remove <UID>');
  }

  ensureAppInitialized();
  const record = await admin.auth().getUser(uid);
  const claims = { ...(record.customClaims || {}) };
  delete claims.admin;
  delete claims.roles;
  delete claims.permissions;
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
          roles: user.customClaims.roles || [],
          permissions: user.customClaims.permissions || [],
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
    const roles =
      Array.isArray(adminUser.roles) && adminUser.roles.length
        ? adminUser.roles.join(', ')
        : '—';
    const permissions =
      Array.isArray(adminUser.permissions) && adminUser.permissions.length
        ? adminUser.permissions.join(', ')
        : '—';
    console.log(
      `• ${adminUser.uid} (${adminUser.email}) | rôles : ${roles} | permissions : ${permissions}`
    );
  });
}

async function main() {
  const [, , command, uid, ...rest] = process.argv;

  const rolesArg = rest.find((arg) => arg.startsWith('--roles='));
  const permissionsArg = rest.find((arg) =>
    arg.startsWith('--permissions=')
  );

  const parseList = (arg) =>
    arg
      ? arg
          .split('=')[1]
          .split(',')
          .map((value) => value.trim())
          .filter(Boolean)
      : undefined;

  const roles = parseList(rolesArg);
  const permissions = parseList(permissionsArg);

  switch (command) {
    case 'add':
      await addAdmin(uid, { roles, permissions });
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
