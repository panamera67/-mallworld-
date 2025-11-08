import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  if (request.nextUrl.pathname.startsWith('/admin')) {
    const adminCookie = request.cookies.get('mw-admin');

    if (!adminCookie || adminCookie.value !== '1') {
      const redirectUrl = new URL('/', request.url);
      redirectUrl.searchParams.set('auth', 'admin');
      return NextResponse.redirect(redirectUrl);
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/admin/:path*'],
};
