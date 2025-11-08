'use client';

import {
  GoogleAuthProvider,
  User,
  signInWithEmailAndPassword,
  signInWithPopup,
  signOut,
  updateProfile,
  onAuthStateChanged,
} from 'firebase/auth';
import {
  PropsWithChildren,
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';
import { auth } from '../lib/firebase';

type AuthContextValue = {
  user: User | null;
  isAdmin: boolean;
  loading: boolean;
  signInWithGoogle: () => Promise<void>;
  signInWithEmail: (email: string, password: string) => Promise<User>;
  signOutUser: () => Promise<void>;
  refreshClaims: () => Promise<void>;
  updateDisplayName: (displayName: string) => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

async function syncAdminSession(user: User | null, isAdmin: boolean) {
  try {
    if (user && isAdmin) {
      const idToken = await user.getIdToken();
      await fetch('/api/admin-session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idToken }),
      });
    } else {
      await fetch('/api/admin-session', { method: 'DELETE' });
    }
  } catch (error) {
    console.error('Erreur lors de la synchronisation de session admin:', error);
  }
}

export function AuthProvider({ children }: PropsWithChildren) {
  const [user, setUser] = useState<User | null>(null);
  const [isAdmin, setIsAdmin] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      setUser(firebaseUser);

      if (!firebaseUser) {
        setIsAdmin(false);
        setLoading(false);
        return;
      }

      try {
        const tokenResult = await firebaseUser.getIdTokenResult(true);
        setIsAdmin(Boolean(tokenResult.claims?.admin));
      } catch (error) {
        console.error("Impossible de récupérer les claims de l'utilisateur:", error);
        setIsAdmin(false);
      } finally {
        setLoading(false);
      }
    });

    return () => unsubscribe();
  }, []);

  useEffect(() => {
    if (!loading) {
      void syncAdminSession(user, isAdmin);
    }
  }, [user, isAdmin, loading]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAdmin,
      loading,
      signInWithGoogle: async () => {
        const provider = new GoogleAuthProvider();
        await signInWithPopup(auth, provider);
      },
      signInWithEmail: async (email: string, password: string) => {
        const credential = await signInWithEmailAndPassword(auth, email, password);
        return credential.user;
      },
      signOutUser: async () => {
        await signOut(auth);
        await syncAdminSession(null, false);
      },
      refreshClaims: async () => {
        if (!user) return;
        const tokenResult = await user.getIdTokenResult(true);
        setIsAdmin(Boolean(tokenResult.claims?.admin));
      },
      updateDisplayName: async (displayName: string) => {
        if (!user) return;
        await updateProfile(user, { displayName });
        setUser(auth.currentUser);
      },
    }),
    [user, isAdmin, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth doit être utilisé à l’intérieur de <AuthProvider>.');
  }
  return context;
}
