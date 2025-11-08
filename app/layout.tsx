import type { Metadata } from 'next';
import { AuthProvider } from '../context/AuthContext';
import Navbar from '../components/Navbar';

export const metadata: Metadata = {
  title: 'MallWorld v2.3',
  description: 'Plateforme omnicanal pour centres commerciaux et expériences retail.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr">
      <body className="bg-gray-50 text-gray-900 antialiased">
        <AuthProvider>
          <Navbar />
          <main className="mx-auto min-h-screen max-w-6xl px-4 py-8">
            {children}
          </main>
        </AuthProvider>
      </body>
    </html>
  );
}
