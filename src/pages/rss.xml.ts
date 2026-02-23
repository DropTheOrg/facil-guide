import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';

export const GET: APIRoute = async () => {
  const allGuides = await getCollection('guides');
  const enGuides = allGuides
    .filter((g) => g.data.lang === 'en')
    .sort((a, b) => new Date(b.data.date).getTime() - new Date(a.data.date).getTime());

  const items = enGuides.map((guide) => {
    const slugParts = guide.id.split('/');
    const slug = slugParts[slugParts.length - 1].replace(/\.md$/, '');
    const url = `https://facil.guide/en/guide/${slug}/`;
    return `    <item>
      <title>${escapeXml(guide.data.title)}</title>
      <link>${url}</link>
      <guid>${url}</guid>
      <description>${escapeXml(guide.data.description)}</description>
      <pubDate>${new Date(guide.data.date).toUTCString()}</pubDate>
      <category>${guide.data.category}</category>
    </item>`;
  });

  const rss = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>facil.guide</title>
    <description>Simple step-by-step technology guides to help your family master technology.</description>
    <link>https://facil.guide/en/</link>
    <atom:link href="https://facil.guide/rss.xml" rel="self" type="application/rss+xml" />
    <language>en</language>
    <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>
${items.join('\n')}
  </channel>
</rss>`;

  return new Response(rss, {
    headers: { 'Content-Type': 'application/xml; charset=utf-8' },
  });
};

function escapeXml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}
