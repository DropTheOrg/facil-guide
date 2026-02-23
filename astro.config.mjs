import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://facil.guide',
  output: 'static',
  integrations: [
    sitemap({
      i18n: {
        defaultLocale: 'en',
        locales: {
          en: 'en',
          fr: 'fr',
          es: 'es',
          pt: 'pt',
          it: 'it',
        },
      },
    }),
  ],
  i18n: {
    defaultLocale: 'fr',
    locales: ['fr', 'en', 'es', 'pt', 'it'],
    routing: {
      prefixDefaultLocale: true,
      redirectToDefaultLocale: false,
    },
  },
});
