/**
 * Cloudflare Pages Middleware: Geo-based language routing
 *
 * - Detects visitor country via request.cf.country
 * - Rewrites to the correct language version
 * - Senior never sees language codes in URL
 * - Cookie override for manual language switch
 * - Accept-Language fallback for VPN/multilingual countries
 */

const COUNTRY_TO_LANG = {
  // French
  FR: 'fr', MC: 'fr', SN: 'fr', CI: 'fr', ML: 'fr', BF: 'fr', NE: 'fr',
  TD: 'fr', CF: 'fr', CG: 'fr', GA: 'fr', DJ: 'fr', KM: 'fr', MG: 'fr',
  // Spanish
  ES: 'es', MX: 'es', AR: 'es', CO: 'es', CL: 'es', PE: 'es', VE: 'es',
  EC: 'es', GT: 'es', CU: 'es', BO: 'es', DO: 'es', HN: 'es', PY: 'es',
  SV: 'es', NI: 'es', CR: 'es', PA: 'es', UY: 'es', GQ: 'es',
  // Portuguese
  PT: 'pt', BR: 'pt', AO: 'pt', MZ: 'pt', CV: 'pt', GW: 'pt', ST: 'pt', TL: 'pt',
  // Italian
  IT: 'it', SM: 'it', VA: 'it',
};

// Countries where we need Accept-Language tiebreaker
const MULTILINGUAL_COUNTRIES = ['BE', 'CH', 'CA', 'LU', 'AD'];

const SUPPORTED_LANGS = ['en', 'fr', 'es', 'pt', 'it'];

function detectLangFromAcceptLanguage(header) {
  if (!header) return null;
  // Parse Accept-Language: fr-FR,fr;q=0.9,en;q=0.8
  const langs = header.split(',').map(part => {
    const [lang, qPart] = part.trim().split(';');
    const q = qPart ? parseFloat(qPart.split('=')[1]) : 1;
    const code = lang.trim().split('-')[0].toLowerCase();
    return { code, q };
  }).sort((a, b) => b.q - a.q);

  for (const { code } of langs) {
    if (SUPPORTED_LANGS.includes(code)) return code;
  }
  return null;
}

export async function onRequest(context) {
  const { request } = context;
  const url = new URL(request.url);
  const path = url.pathname;

  // Skip: already has a language prefix
  if (/^\/(en|fr|es|pt|it)\//.test(path) || /^\/(en|fr|es|pt|it)$/.test(path)) {
    return context.next();
  }

  // Skip: API routes
  if (path.startsWith('/api/')) {
    return context.next();
  }

  // Skip: static assets, sitemaps, robots
  if (/\.(js|css|png|jpg|jpeg|gif|svg|webp|woff2?|ico|xml|txt|json)$/i.test(path)) {
    return context.next();
  }

  // Skip: root index (homepage has its own routing)
  if (path === '/' || path === '') {
    // For homepage, redirect to language version
    const lang = resolveLang(request);
    return Response.redirect(new URL(`/${lang}/`, url.origin), 302);
  }

  // Resolve language
  const lang = resolveLang(request);

  // Rewrite the URL to include language prefix
  const newPath = `/${lang}${path.endsWith('/') ? path : path + '/'}`;
  const newUrl = new URL(newPath, url.origin);
  newUrl.search = url.search;

  // Fetch the language-specific page
  const response = await context.env.ASSETS.fetch(new Request(newUrl, request));

  // If 404, try English as fallback
  if (response.status === 404 && lang !== 'en') {
    const fallbackUrl = new URL(`/en${path.endsWith('/') ? path : path + '/'}`, url.origin);
    const fallback = await context.env.ASSETS.fetch(new Request(fallbackUrl, request));
    if (fallback.status === 200) return fallback;
  }

  return response;
}

function resolveLang(request) {
  // 1. Cookie override (user manually switched language)
  const cookies = request.headers.get('Cookie') || '';
  const langCookie = cookies.match(/facil_lang=([a-z]{2})/);
  if (langCookie && SUPPORTED_LANGS.includes(langCookie[1])) {
    return langCookie[1];
  }

  // 2. Geo detection
  const country = request.cf?.country;

  // 3. For multilingual countries, use Accept-Language
  if (country && MULTILINGUAL_COUNTRIES.includes(country)) {
    const fromHeader = detectLangFromAcceptLanguage(
      request.headers.get('Accept-Language')
    );
    if (fromHeader) return fromHeader;
  }

  // 4. Country mapping
  if (country && COUNTRY_TO_LANG[country]) {
    return COUNTRY_TO_LANG[country];
  }

  // 5. Accept-Language fallback (VPN users, unknown countries)
  const fromHeader = detectLangFromAcceptLanguage(
    request.headers.get('Accept-Language')
  );
  if (fromHeader) return fromHeader;

  // 6. Default to English
  return 'en';
}
