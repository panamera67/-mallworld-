import { NextResponse } from 'next/server';
import { getFirebaseAdminAuth } from '../../../lib/firebaseAdmin';

export const runtime = 'nodejs';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const idToken: string | undefined = body?.idToken;

    if (!idToken) {
      return NextResponse.json(
        { error: 'ID token manquant.' },
        { status: 400 }
      );
    }

    const auth = getFirebaseAdminAuth();
    const decodedToken = await auth.verifyIdToken(idToken, true);

    if (!decodedToken.admin) {
      return NextResponse.json(
        { error: 'Utilisateur non autorisé.' },
        { status: 403 }
      );
    }

    const response = NextResponse.json({ status: 'ok' });
    response.cookies.set({
      name: 'mw-admin',
      value: '1',
      httpOnly: true,
      secure: true,
      sameSite: 'lax',
      path: '/',
      maxAge: 60 * 60 * 24 * 5, // 5 jours
    });

    return response;
  } catch (error) {
    console.error('POST /api/admin-session error:', error);
    return NextResponse.json({ error: 'Token invalide.' }, { status: 401 });
  }
}

export async function DELETE() {
  const response = NextResponse.json({ status: 'cleared' });
  response.cookies.set({
    name: 'mw-admin',
    value: '',
    httpOnly: true,
    secure: true,
    sameSite: 'lax',
    path: '/',
    maxAge: 0,
  });
  return response;
}
