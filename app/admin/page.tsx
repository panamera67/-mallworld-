'use client';

import { useEffect, useState } from 'react';
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
    signInWithGoogle,
    signOutUser,
  } = useAuth();
  const [events, setEvents] = useState<MallEvent[]>([]);
  const [eventsLoading, setEventsLoading] = useState(true);
  const [form, setForm] = useState<MallEvent>({
    mall: '',
    title: '',
    date: '',
    type: '',
  });
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState<boolean>(false);

  useEffect(() => {
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
  }, []);

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

    if (authLoading) {
    return <div className="p-6">Chargement…</div>;
  }

  return (
    <div className="mx-auto max-w-4xl p-6">
      <h1 className="text-2xl font-bold mb-6">Dashboard Admin · MallWorld</h1>

      {!user ? (
        <button
          onClick={loginWithGoogle}
          className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
        >
          Connexion Google
        </button>
      ) : (
        <div className="mb-4 flex items-center justify-between rounded border border-gray-200 bg-gray-50 p-3">
          <div>
            <p className="font-medium">{user.email}</p>
            <p className="text-sm text-gray-600">
              Statut : {isAdmin ? 'Admin' : 'Utilisateur standard'}
            </p>
          </div>
          <button
            onClick={logout}
            className="rounded border border-gray-400 px-3 py-1 text-gray-700 hover:bg-gray-200"
          >
            Déconnexion
          </button>
        </div>
      )}

        {error && <p className="mb-4 text-sm text-red-600">{error}</p>}

        {isAdmin ? (
          <div className="grid gap-8 md:grid-cols-2">
            <section className="rounded border border-gray-200 p-4 shadow-sm">
              <h2 className="mb-4 text-lg font-semibold">
                Ajouter un événement
              </h2>
              <div className="flex flex-col gap-3">
                <input
                  className="rounded border border-gray-300 px-3 py-2"
                  placeholder="Centre commercial"
                  value={form.mall}
                  onChange={(event) =>
                    setForm((prev) => ({ ...prev, mall: event.target.value }))
                  }
                />
                <input
                  className="rounded border border-gray-300 px-3 py-2"
                  placeholder="Titre"
                  value={form.title}
                  onChange={(event) =>
                    setForm((prev) => ({ ...prev, title: event.target.value }))
                  }
                />
                <input
                  className="rounded border border-gray-300 px-3 py-2"
                  type="date"
                  value={form.date}
                  onChange={(event) =>
                    setForm((prev) => ({ ...prev, date: event.target.value }))
                  }
                />
                <input
                  className="rounded border border-gray-300 px-3 py-2"
                  placeholder="Type (promo, animation, etc.)"
                  value={form.type}
                  onChange={(event) =>
                    setForm((prev) => ({ ...prev, type: event.target.value }))
                  }
                />
                <button
                  onClick={() => addEvent(form)}
                  disabled={saving}
                  className="rounded bg-green-600 px-4 py-2 text-white hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {saving ? 'Ajout en cours…' : 'Ajouter'}
                </button>
              </div>
            </section>

            <section className="rounded border border-gray-200 p-4 shadow-sm">
              <h2 className="mb-4 text-lg font-semibold">
                Gestion des événements
              </h2>

              <div className="flex max-h-[400px] flex-col gap-3 overflow-y-auto pr-2">
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
                      className="rounded border border-gray-300 p-3"
                    >
                      <header className="mb-2 flex items-center justify-between">
                        <div>
                          <p className="font-semibold">{event.title}</p>
                          <p className="text-sm text-gray-600">{event.mall}</p>
                        </div>
                        <button
                          onClick={() => removeEvent(event.id!)}
                          className="rounded border border-red-500 px-2 py-1 text-red-600 hover:bg-red-50"
                        >
                          Supprimer
                        </button>
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
                          className="rounded border border-blue-500 px-3 py-1 text-blue-600 hover:bg-blue-50"
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
                          className="rounded border border-indigo-500 px-3 py-1 text-indigo-600 hover:bg-indigo-50"
                        >
                          Modifier la date
                        </button>
                      </footer>
                    </article>
                  ))
                )}
              </div>
            </section>
          </div>
        ) : (
          <p className="rounded border border-yellow-400 bg-yellow-50 p-3 text-sm text-yellow-700">
            Accès restreint : demande à un administrateur de t’accorder le rôle
            admin.
          </p>
        )}

      <section className="mt-10 rounded border border-gray-200 p-4 text-sm text-gray-600">
        <h2 className="mb-2 text-base font-semibold">Guide rapide</h2>
        <ul className="list-disc space-y-1 pl-5">
          <li>
            Crée un utilisateur dans Firebase Auth et assigne-lui la claim{' '}
            <code>admin</code>.
          </li>
          <li>
            Les règles Firestore empêchent toute écriture tant que la claim
            n’est pas active.
          </li>
          <li>
            Les champs <code>created_at</code> et <code>updated_at</code> sont
            gérés automatiquement.
          </li>
        </ul>
      </section>
    </div>
  );
}
