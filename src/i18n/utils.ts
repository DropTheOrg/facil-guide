import type { Lang } from './translations';

const allLangs: Lang[] = ['fr', 'en', 'es', 'pt', 'it'];

export function getLangFromUrl(url: URL): Lang {
  const [, lang] = url.pathname.split('/');
  if (allLangs.includes(lang as Lang)) {
    return lang as Lang;
  }
  return 'fr';
}

export function getLocalizedPath(lang: Lang, path: string): string {
  return `/${lang}${path}`;
}

export function getAlternateUrls(
  currentPath: string,
  currentLang: Lang
): { lang: Lang; url: string }[] {
  const pathWithoutLang = currentPath.replace(`/${currentLang}`, '');
  return allLangs.map((lang) => ({
    lang,
    url: `/${lang}${pathWithoutLang}`,
  }));
}

export function getCategoryIcon(category: string): string {
  const icons: Record<string, string> = {
    smartphone: 'phone',
    ordinateur: 'monitor',
    internet: 'globe',
    applications: 'grid',
    securite: 'shield',
    communication: 'message-circle',
  };
  return icons[category] || 'file-text';
}

export function getCategoryEmoji(category: string): string {
  const emojis: Record<string, string> = {
    smartphone: '\uD83D\uDCF1',
    ordinateur: '\uD83D\uDCBB',
    internet: '\uD83C\uDF10',
    applications: '\uD83D\uDCE6',
    securite: '\uD83D\uDD12',
    communication: '\uD83D\uDCAC',
  };
  return emojis[category] || '\uD83D\uDCC4';
}

export function getPlatformLabel(platform: string): string {
  const labels: Record<string, string> = {
    iphone: 'iPhone',
    android: 'Android',
    web: 'Web',
    windows: 'Windows',
    mac: 'Mac',
  };
  return labels[platform] || platform;
}

export function getStaticLangPaths() {
  return allLangs.map((lang) => ({ params: { lang } }));
}
