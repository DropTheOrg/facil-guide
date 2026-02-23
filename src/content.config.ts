import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const faqItemSchema = z.object({
  question: z.string(),
  answer: z.string(),
});

const guides = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/guides' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    category: z.enum([
      'smartphone',
      'ordinateur',
      'internet',
      'applications',
      'securite',
      'communication',
      'ia',
      'government',
      'money',
      'troubleshooting',
    ]),
    steps: z.number(),
    difficulty: z.enum(['facile', 'moyen', 'avance']),
    platform: z.enum(['iphone', 'android', 'web', 'windows', 'mac', 'all']),
    lang: z.enum(['fr', 'en', 'es', 'pt', 'it']),
    date: z.string(),
    faq: z.array(faqItemSchema).optional(),
    // Country-specific guides: only shown to visitors from these countries
    // Empty/missing = universal (shown to everyone)
    country: z.array(z.string()).optional(),
  }),
});

const reviews = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/reviews' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    productName: z.string(),
    brand: z.string(),
    category: z.enum([
      'smartphone',
      'ordinateur',
      'internet',
      'applications',
      'securite',
      'communication',
      'ia',
      'government',
      'money',
      'troubleshooting',
    ]),
    rating: z.number().min(0).max(5),
    price: z.string(),
    pros: z.array(z.string()),
    cons: z.array(z.string()),
    verdict: z.string(),
    platform: z.enum(['iphone', 'android', 'web', 'windows', 'mac', 'all']).optional(),
    lang: z.enum(['fr', 'en', 'es', 'pt', 'it']),
    date: z.string(),
    faq: z.array(faqItemSchema).optional(),
  }),
});

const comparisons = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/comparisons' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    productA: z.object({
      name: z.string(),
      brand: z.string(),
      price: z.string(),
    }),
    productB: z.object({
      name: z.string(),
      brand: z.string(),
      price: z.string(),
    }),
    category: z.enum([
      'smartphone',
      'ordinateur',
      'internet',
      'applications',
      'securite',
      'communication',
      'ia',
      'government',
      'money',
      'troubleshooting',
    ]),
    winner: z.string().optional(),
    recommendation: z.string(),
    lang: z.enum(['fr', 'en', 'es', 'pt', 'it']),
    date: z.string(),
    faq: z.array(faqItemSchema).optional(),
  }),
});

export const collections = { guides, reviews, comparisons };
