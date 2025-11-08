'use client';

import Link from 'next/link';
import { useState } from 'react';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const {
    user,
    loading,
    isAdmin,
    roles,
    signInWithGoogle,
    signOutUser,
  } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);

  async function handleLogin() {
    try {
      await signInWithGoogle();
    } catch (error) {
      console.error('Erreur lors de la connexion Google:', error);
    }
  }

  async function handleLogout() {
    try {
      await signOutUser();
    } catch (error) {
      console.error('Erreur lors de la déconnexion:', error);
    } finally {
      setMenuOpen(false);
    }
  }

  return (
    <header className="border-b bg-white shadow-sm">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link href="/" className="text-xl font-bold text-indigo-600">
          MallWorld
        </Link>

        <nav className="flex items-center gap-4">
          {isAdmin && (
            <Link
              href="/admin"
              className="rounded-full border border-indigo-500 px-3 py-1 text-sm font-medium text-indigo-600 hover:bg-indigo-50"
            >
              Dashboard Admin
            </Link>
          )}

          {loading ? (
            <span className="text-sm text-gray-500">Chargement…</span>
          ) : user ? (
            <div className="relative">
              <button
                onClick={() => setMenuOpen((prev) => !prev)}
                className="flex items-center gap-2 rounded-full border border-gray-200 bg-gray-50 px-3 py-2 hover:bg-gray-100"
              >
                {user.photoURL ? (
                  <img
                    src={user.photoURL}
                    alt={user.displayName || user.email || 'Utilisateur'}
                    className="h-8 w-8 rounded-full object-cover"
                  />
                ) : (
                  <span className="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-500 text-sm font-semibold text-white">
                    {(user.displayName || user.email || 'U')
                      .substring(0, 2)
                      .toUpperCase()}
                  </span>
                )}
                <span className="text-sm font-medium text-gray-700">
                  {user.displayName || user.email}
                </span>
              </button>

              {menuOpen && (
                <div className="absolute right-0 z-20 mt-2 w-48 rounded-lg border border-gray-200 bg-white py-2 shadow-lg">
                  <p className="px-4 pb-2 text-xs text-gray-500">Connecté</p>
                  <div className="px-4 pb-2 text-sm text-gray-700">
                    {user.email}
                  </div>
                  {isAdmin && (
                    <div className="px-4 pb-2 text-xs uppercase tracking-wide text-indigo-500">
                      Admin
                    </div>
                  )}
                  {roles.length > 0 && (
                    <div className="px-4 pb-2 text-xs text-gray-500">
                      Rôles :{' '}
                      <span className="font-medium text-gray-700">
                        {roles.join(', ')}
                      </span>
                    </div>
                  )}
                  <button
                    onClick={handleLogout}
                    className="block w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50"
                  >
                    Se déconnecter
                  </button>
                </div>
              )}
            </div>
          ) : (
            <button
              onClick={handleLogin}
              className="rounded-full bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
            >
              Connexion
            </button>
          )}
        </nav>
      </div>
    </header>
  );
}
