import type { Metadata } from 'next';

export interface SEOProps {
  title?: string;
  description?: string;
  canonical?: string;
  openGraph?: {
    type?: 'website' | 'article';
    images?: string[];
  };
  twitter?: {
    card?: 'summary' | 'summary_large_image';
  };
}

export function generateMetadata({
  title,
  description = 'Social Media Management Bot - Streamline your social media presence with automated posting, scheduling, and analytics.',
  canonical,
  openGraph,
  twitter,
}: SEOProps = {}): Metadata {
  const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000';
  const fullTitle = title ? `${title} | Social Media Management Bot` : 'Social Media Management Bot';

  return {
    title: fullTitle,
    description,
    metadataBase: new URL(baseUrl),
    alternates: {
      canonical: canonical ? `${baseUrl}${canonical}` : baseUrl,
    },
    openGraph: {
      title: fullTitle,
      description,
      url: canonical ? `${baseUrl}${canonical}` : baseUrl,
      siteName: 'Social Media Management Bot',
      type: openGraph?.type || 'website',
      images: openGraph?.images || [`${baseUrl}/og-image.jpg`],
    },
    twitter: {
      card: twitter?.card || 'summary_large_image',
      title: fullTitle,
      description,
      images: openGraph?.images || [`${baseUrl}/og-image.jpg`],
    },
    robots: {
      index: true,
      follow: true,
    },
  };
}

export function generateStructuredData() {
  const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000';
  
  return {
    '@context': 'https://schema.org',
    '@type': 'WebApplication',
    name: 'Social Media Management Bot',
    description: 'Streamline your social media presence with automated posting, scheduling, and analytics.',
    url: baseUrl,
    applicationCategory: 'BusinessApplication',
    operatingSystem: 'Web Browser',
    offers: {
      '@type': 'Offer',
      price: '0',
      priceCurrency: 'USD',
    },
  };
}