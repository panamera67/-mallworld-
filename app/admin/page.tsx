'use client';

import { useEffect, useMemo, useState } from 'react';
import {
  addDoc,
  collection,
  deleteDoc,
  doc,
  onSnapshot,
  orderBy,
  query,
  updateDoc,
} from 'firebase/firestore';
import AdminSidebar from '../../components/AdminSidebar';
import { useAuth } from '../../context/AuthContext';
import { db } from '../../lib/firebase';

type MallEvent = {
  id?: string;
  mall: string;
  title: string;
  date: string;
  type: string;
  created_at?: string;
  updated_at?: string;
};

type RawSidebarItem = {
  key: string;
  label: string;
  description?: string;
  icon?: string;
  requiredPermissions?: string[];
  requiredRoles?: string[];
};

type SidebarItem = RawSidebarItem & {
  disabled: boolean;
  lockedReason?: string;
};

function formatDate(date: string | undefined) {
  if (!date) return '';
  const parsed = new Date(date);
  if (Number.isNaN(parsed.getTime())) return date;
  return parsed.toLocaleDateString();
}

export default function AdminDashboardPage() {
  const {
    user,
    isAdmin,
    loading: authLoading,
    roles,
    permissions,
    hasPermission,
    hasRole,
    signInWithGoogle,
    signOutUser,
  } = useAuth();

  const [events, setEvents] = useState<MallEvent[]>([]);
  const [eventsLoading, setEventsLoading] = useState<boolean>(true);
  const [form, setForm] = useState<MallEvent>({
    mall: '',
    title: '',
    date: '',
    type: '',
  });
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState<boolean>(false);
  const [activeSection, setActiveSection] = useState<string | null>(null);

  const hasGranularRules = permissions.length > 0 || roles.length > 0;
  const hasSuperAdmin = hasRole('superadmin');

  const canViewEvents = !hasGranularRules
    ? isAdmin
    : hasSuperAdmin || hasPermission('events:read');
  const canManageEvents = !hasGranularRules
    ? isAdmin
    : hasSuperAdmin || hasPermission('events:write');
  const canManageTeam = !hasGranularRules
    ? isAdmin
    : hasSuperAdmin || hasPermission('team:write') || hasRole('team-admin');
  const canAccessSettings = !hasGranularRules
    ? isAdmin
    : hasSuperAdmin || hasPermission('settings:manage');

  useEffect(() => {
    if (!canViewEvents) {
      setEvents([]);
      setEventsLoading(false);
      return;
    }

    setEventsLoading(true);

    const eventsQuery = query(
      collection(db, 'mall_events'),
      orderBy('date', 'desc')
    );

    const unsubscribe = onSnapshot(
      eventsQuery,
      (snapshot) => {
        const items: MallEvent[] = [];
        snapshot.forEach((item) => {
          const data = item.data() as MallEvent;
          items.push({
            ...data,
            id: item.id,
          });
        });
        setEvents(items);
        setEventsLoading(false);
      },
      (err) => {
        console.error('Erreur Firestore', err);
        setError("Impossible de récupérer les événements.");
        setEvents([]);
        setEventsLoading(false);
      }
    );

    return () => unsubscribe();
  }, [canViewEvents]);

  const rawSidebarItems = useMemo<RawSidebarItem[]>(
    () => [
      {
        key: 'overview',
        label: "Vue d'ensemble",
        description: 'Indicateurs temps réel & santé des opérations',
        icon: '📊',
        requiredPermissions: ['events:read'],
      },
      {
        key: 'events',
        label: 'Événements & campagnes',
        description: 'Programmation locale et promotions géolocalisées',
        icon: '🗓️',
        requiredPermissions: ['events:read'],
      },
      {
        key: 'team',
        label: 'Équipe & rôles',
        description: 'Gestion des droits malls & managers',
        icon: '👥',
        requiredRoles: ['superadmin'],
        requiredPermissions: ['team:read'],
      },
      {
        key: 'settings',
        label: 'Paramètres & intégrations',
        description: 'Automatisations, webhooks et API partenaires',
        icon: '⚙️',
        requiredRoles: ['superadmin'],
        requiredPermissions: ['settings:manage'],
      },
    ],
    []
  );

  const sidebarItems = useMemo<SidebarItem[]>(() => {
    return rawSidebarItems.map((item) => {
      const requiredPermissions = hasGranularRules
        ? item.requiredPermissions ?? []
        : [];
      const requiredRoles = hasGranularRules ? item.requiredRoles ?? [] : [];

      const meetsPermissions =
        requiredPermissions.length === 0 ||
        requiredPermissions.every(
          (permission) => hasSuperAdmin || hasPermission(permission)
        );

      const meetsRoles =
        requiredRoles.length === 0 ||
        requiredRoles.some((role) => hasRole(role));

      const accessible = !hasGranularRules
        ? isAdmin
        : meetsPermissions && meetsRoles;

      let lockedReason: string | undefined;
      if (!accessible) {
        const reasons: string[] = [];
        if (!meetsPermissions && requiredPermissions.length) {
          reasons.push(`Permissions: ${requiredPermissions.join(', ')}`);
        }
        if (!meetsRoles && requiredRoles.length) {
          reasons.push(`Rôles: ${requiredRoles.join(', ')}`);
        }
        if (!reasons.length) {
          reasons.push('Accès restreint aux administrateurs avancés.');
        }
        lockedReason = reasons.join(' · ');
      }

      return {
        ...item,
        disabled: !accessible,
        lockedReason,
      };
    });
  }, [
    rawSidebarItems,
    hasGranularRules,
    hasPermission,
    hasRole,
    hasSuperAdmin,
    isAdmin,
  ]);

  const accessibleItems = useMemo(
    () => sidebarItems.filter((item) => !item.disabled),
    [sidebarItems]
  );
  const firstAccessibleKey = accessibleItems[0]?.key ?? null;

  useEffect(() => {
    if (
      !activeSection ||
      sidebarItems.every(
        (item) => item.key !== activeSection || item.disabled
      )
    ) {
      setActiveSection(firstAccessibleKey);
    }
  }, [activeSection, firstAccessibleKey, sidebarItems]);

  const upcomingEventsCount = canViewEvents
    ? events.filter((event) => {
        try {
          return new Date(event.date) >= new Date();
        } catch {
          return false;
        }
      }).length
    : 0;

  const mallsTracked = canViewEvents
    ? new Set(events.map((event) => event.mall)).size
    : 0;

  async function loginWithGoogle() {
    setError(null);
    try {
      await signInWithGoogle();
    } catch (err) {
      console.error('Erreur de connexion', err);
      setError('Impossible de se connecter pour le moment.');
    }
  }

  async function logout() {
    setError(null);
    try {
      await signOutUser();
    } catch (err) {
      console.error('Erreur lors de la déconnexion', err);
      setError('Impossible de se déconnecter pour le moment.');
    }
  }

  async function addEvent(submission: MallEvent) {
    if (!canManageEvents) {
      setError("Vous n'avez pas la permission d'ajouter des événements.");
      return;
    }

    const { mall, title, date, type } = submission;
    if (!mall || !title || !date || !type) {
      setError('Tous les champs sont requis pour créer un événement.');
      return;
    }

    setSaving(true);
    setError(null);

    try {
      await addDoc(collection(db, 'mall_events'), {
        mall,
        title,
        date,
        type,
        created_at: new Date().toISOString(),
      });
      setForm({ mall: '', title: '', date: '', type: '' });
    } catch (err) {
      console.error('Erreur lors de la création', err);
      setError("Impossible d'ajouter l'événement.");
    } finally {
      setSaving(false);
    }
  }

  async function updateEvent(id: string, patch: Partial<MallEvent>) {
    if (!canManageEvents) {
      setError("Vous n'avez pas la permission de modifier des événements.");
      return;
    }

    setError(null);
    try {
      await updateDoc(doc(db, 'mall_events', id), {
        ...patch,
        updated_at: new Date().toISOString(),
      });
    } catch (err) {
      console.error('Erreur lors de la mise à jour', err);
      setError("Impossible de modifier l'événement.");
    }
  }

  async function removeEvent(id: string) {
    if (!canManageEvents) {
      setError("Vous n'avez pas la permission de supprimer des événements.");
      return;
    }

    const confirmation = window.confirm(
      'Supprimer définitivement cet événement ?'
    );
    if (!confirmation) return;

    setError(null);
    try {
      await deleteDoc(doc(db, 'mall_events', id));
    } catch (err) {
      console.error('Erreur lors de la suppression', err);
      setError("Impossible de supprimer l'événement.");
    }
  }

  function renderOverviewSection() {
    return (
      <div className="space-y-4">
        <section className="grid gap-4 sm:grid-cols-2">
          <div className="rounded-lg border border-indigo-100 bg-white p-5 shadow-sm">
            <p className="text-sm font-medium text-indigo-600">
              Événements actifs
            </p>
            <p className="mt-2 text-3xl font-bold text-gray-900">
              {eventsLoading ? '—' : upcomingEventsCount}
            </p>
            <p className="mt-1 text-xs text-gray-500">
              Prévu sur les 30 prochains jours
            </p>
          </div>
          <div className="rounded-lg border border-indigo-100 bg-white p-5 shadow-sm">
            <p className="text-sm font-medium text-indigo-600">
              Malls synchronisés
            </p>
            <p className="mt-2 text-3xl font-bold text-gray-900">
              {eventsLoading ? '—' : mallsTracked}
            </p>
            <p className="mt-1 text-xs text-gray-500">
              Centres commerciaux avec programmation active
            </p>
          </div>
        </section>

        <section className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900">
            Priorités opérationnelles
          </h3>
          <ul className="mt-3 space-y-2 text-sm text-gray-600">
            <li>
              • Vérifier les animations des 7 prochains jours et les stocks
              associés.
            </li>
            <li>
              • Synchroniser les campagnes offline/online dans Supabase et
              Stripe.
            </li>
            <li>
              • Valider la programmation saisonnière (Noël, Soldes, Ramadan, etc.).
            </li>
          </ul>
        </section>
      </div>
    );
  }

  function renderEventsSection() {
    if (!canViewEvents) {
      return (
        <div className="rounded border border-yellow-400 bg-yellow-50 p-4 text-sm text-yellow-700">
          Vous n&rsquo;avez pas la permission de consulter les événements de ce
          mall.
        </div>
      );
    }

    return (
      <div className="space-y-6">
        <section className="rounded border border-gray-200 bg-white p-5 shadow-sm">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">
              Ajouter un événement
            </h2>
            {!canManageEvents && (
              <span className="rounded-full border border-amber-300 bg-amber-50 px-3 py-1 text-xs font-medium text-amber-700">
                Lecture seule
              </span>
            )}
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            <input
              className="rounded border border-gray-300 px-3 py-2"
              placeholder="Centre commercial"
              value={form.mall}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, mall: event.target.value }))
              }
              disabled={!canManageEvents || saving}
            />
            <input
              className="rounded border border-gray-300 px-3 py-2"
              placeholder="Titre"
              value={form.title}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, title: event.target.value }))
              }
              disabled={!canManageEvents || saving}
            />
            <input
              className="rounded border border-gray-300 px-3 py-2"
              type="date"
              value={form.date}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, date: event.target.value }))
              }
              disabled={!canManageEvents || saving}
            />
            <input
              className="rounded border border-gray-300 px-3 py-2"
              placeholder="Type (promo, animation, etc.)"
              value={form.type}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, type: event.target.value }))
              }
              disabled={!canManageEvents || saving}
            />
          </div>
          <button
            onClick={() => addEvent(form)}
            disabled={!canManageEvents || saving}
            className="mt-4 inline-flex items-center justify-center rounded bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {saving ? 'Ajout en cours…' : 'Ajouter'}
          </button>
        </section>

        <section className="rounded border border-gray-200 bg-white p-5 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">
            Gestion des événements
          </h2>

          <div className="flex max-h-[420px] flex-col gap-3 overflow-y-auto pr-2">
            {eventsLoading ? (
              <p className="text-sm text-gray-500">
                Chargement des événements…
              </p>
            ) : events.length === 0 ? (
              <p className="text-sm text-gray-500">
                Aucun événement enregistré pour le moment.
              </p>
            ) : (
              events.map((event) => (
                <article
                  key={event.id}
                  className="rounded border border-gray-300 bg-white p-4 shadow-sm"
                >
                  <header className="mb-2 flex flex-col gap-1 md:flex-row md:items-center md:justify-between">
                    <div>
                      <p className="text-base font-semibold text-gray-900">
                        {event.title}
                      </p>
                      <p className="text-sm text-gray-500">{event.mall}</p>
                    </div>
                    {canManageEvents && (
                      <button
                        onClick={() => removeEvent(event.id!)}
                        className="mt-2 inline-flex items-center justify-center rounded border border-red-500 px-2 py-1 text-sm text-red-600 hover:bg-red-50 md:mt-0"
                      >
                        Supprimer
                      </button>
                    )}
                  </header>

                  <dl className="text-sm text-gray-700">
                    <div className="flex gap-2">
                      <dt className="font-medium">Date :</dt>
                      <dd>{formatDate(event.date)}</dd>
                    </div>
                    <div className="flex gap-2">
                      <dt className="font-medium">Type :</dt>
                      <dd>{event.type}</dd>
                    </div>
                  </dl>

                  {canManageEvents && (
                    <footer className="mt-3 flex gap-2">
                      <button
                        onClick={() => {
                          const newTitle = window.prompt(
                            'Nouveau titre',
                            event.title
                          );
                          if (!newTitle) return;
                          updateEvent(event.id!, { title: newTitle });
                        }}
                        className="rounded border border-blue-500 px-3 py-1 text-sm text-blue-600 hover:bg-blue-50"
                      >
                        Renommer
                      </button>
                      <button
                        onClick={() => {
                          const newDate = window.prompt(
                            'Nouvelle date (YYYY-MM-DD)',
                            event.date
                          );
                          if (!newDate) return;
                          updateEvent(event.id!, { date: newDate });
                        }}
                        className="rounded border border-indigo-500 px-3 py-1 text-sm text-indigo-600 hover:bg-indigo-50"
                      >
                        Modifier la date
                      </button>
                    </footer>
                  )}
                </article>
              ))
            )}
          </div>
        </section>
      </div>
    );
  }

  function renderTeamSection() {
    if (!canManageTeam) {
      return (
        <div className="rounded border border-yellow-200 bg-yellow-50 p-4 text-sm text-yellow-700">
          Accès restreint. Seuls les superadmins ou les responsables équipe
          peuvent gérer les rôles.
        </div>
      );
    }

    return (
      <div className="space-y-4">
        <section className="rounded border border-gray-200 bg-white p-5 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900">
            Ajouter un manager de mall
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Utilise le script{' '}
            <code className="rounded bg-gray-100 px-2 py-1">
              node scripts/setAdminClaim.js add &lt;UID&gt; --roles=mall-manager
              --permissions=events:read
            </code>{' '}
            pour attribuer des roles et permissions granulaires.
          </p>
        </section>

        <section className="rounded border border-gray-200 bg-white p-5 shadow-sm">
          <h3 className="text-base font-semibold text-gray-900">
            Modèle de permissions recommandé
          </h3>
          <ul className="mt-3 space-y-2 text-sm text-gray-600">
            <li>
              • <strong>mall-manager</strong> → permissions :{' '}
              <code>events:read</code>, <code>events:write</code>
            </li>
            <li>
              • <strong>marketing</strong> → permissions :{' '}
              <code>events:read</code>
            </li>
            <li>
              • <strong>superadmin</strong> → toutes les permissions +{' '}
              <code>settings:manage</code>
            </li>
          </ul>
        </section>
      </div>
    );
  }

  function renderSettingsSection() {
    if (!canAccessSettings) {
      return (
        <div className="rounded border border-red-200 bg-red-50 p-4 text-sm text-red-600">
          Accès refusé. Cette section est réservée aux superadmins ou aux
          utilisateurs disposant de la permission{' '}
          <code className="font-semibold">settings:manage</code>.
        </div>
      );
    }

    return (
      <div className="space-y-4">
        <section className="rounded border border-gray-200 bg-white p-5 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900">
            Intégrations critiques
          </h2>
          <ul className="mt-3 space-y-2 text-sm text-gray-600">
            <li>• Stripe : webhooks, clés live/test, plans et coupons.</li>
            <li>
              • Supabase : synchronisation des inventaires et des insights
              churn.
            </li>
            <li>• Firebase : règles Firestore & refresh des custom claims.</li>
          </ul>
        </section>

        <section className="rounded border border-gray-200 bg-white p-5 shadow-sm">
          <h3 className="text-base font-semibold text-gray-900">
            Automatisations recommandées
          </h3>
          <p className="mt-2 text-sm text-gray-600">
            Implémente une Cloud Function pour appliquer le rôle{' '}
            <code>mall-manager</code> automatiquement aux emails de ton équipe
            lors de la création de compte. Pense également à consigner les
            actions sensibles (suppression, modification) dans une collection
            d’audit.
          </p>
        </section>
      </div>
    );
  }

  function renderActiveSection() {
    switch (activeSection) {
      case 'events':
        return renderEventsSection();
      case 'team':
        return renderTeamSection();
      case 'settings':
        return renderSettingsSection();
      case 'overview':
      default:
        return renderOverviewSection();
    }
  }

  if (authLoading) {
    return <div className="p-6">Chargement…</div>;
  }

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-6">
      <header>
        <h1 className="text-3xl font-bold text-gray-900">
          Dashboard Admin · MallWorld
        </h1>
        <p className="mt-2 text-sm text-gray-600">
          Pilote les animations locales, les droits équipe et les intégrations
          globales de MallWorld v2.3.
        </p>
      </header>

      {!user ? (
        <button
          onClick={loginWithGoogle}
          className="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          Connexion Google
        </button>
      ) : (
        <div className="flex flex-col gap-3 rounded border border-gray-200 bg-gray-50 p-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="font-medium text-gray-900">{user.email}</p>
            <p className="text-sm text-gray-600">
              Statut : {isAdmin ? 'Admin' : 'Utilisateur standard'}
            </p>
          </div>
          <div className="flex items-center gap-3">
            {(roles.length > 0 || permissions.length > 0) && (
              <div className="text-xs text-gray-500">
                Rôles :{' '}
                <span className="font-medium text-gray-700">
                  {roles.length ? roles.join(', ') : '—'}
                </span>{' '}
                · Permissions :{' '}
                <span className="font-medium text-gray-700">
                  {permissions.length ? permissions.join(', ') : 'héritées'}
                </span>
              </div>
            )}
            <button
              onClick={logout}
              className="rounded border border-gray-400 px-3 py-1 text-sm text-gray-700 hover:bg-gray-200"
            >
              Déconnexion
            </button>
          </div>
        </div>
      )}

      {error && (
        <p className="rounded border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-600">
          {error}
        </p>
      )}

      <div className="flex flex-col gap-6 lg:flex-row">
        <AdminSidebar
          items={sidebarItems.map((item) => ({
            key: item.key,
            label: item.label,
            description: item.description,
            icon: item.icon,
            disabled: item.disabled,
            lockedReason: item.lockedReason,
          }))}
          activeKey={activeSection}
          onSelect={(key) => setActiveSection(key)}
        />

        <section className="flex-1 space-y-6">
          {accessibleItems.length > 0 ? (
            renderActiveSection()
          ) : (
            <div className="rounded border border-yellow-200 bg-yellow-50 p-6 text-sm text-yellow-700">
              Aucun module disponible pour ton profil. Contacte un superadmin
              pour obtenir les permissions nécessaires.
            </div>
          )}
        </section>
      </div>

      <section className="rounded border border-gray-200 bg-white p-5 text-sm text-gray-600 shadow-sm">
        <h2 className="mb-2 text-base font-semibold text-gray-900">
          Guide rapide
        </h2>
        <ul className="list-disc space-y-1 pl-5">
          <li>
            Crée un utilisateur dans Firebase Auth et assigne-lui les claims{' '}
            <code>admin</code>, <code>roles</code>, <code>permissions</code>.
          </li>
          <li>
            Les règles Firestore empêchent toute écriture tant que les claims ne
            sont pas définies (ou que la session admin n’est pas synchronisée).
          </li>
          <li>
            Les champs <code>created_at</code> et <code>updated_at</code> sont
            gérés automatiquement côté Firestore.
          </li>
        </ul>
      </section>
    </div>
  );
}
