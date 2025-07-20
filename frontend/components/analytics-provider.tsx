'use client';

import { useEffect } from 'react';
import Script from 'next/script';

interface AnalyticsProviderProps {
  children: React.ReactNode;
}

declare global {
  interface Window {
    gtag: (...args: unknown[]) => void;
    dataLayer: unknown[];
  }
}

export function AnalyticsProvider({ children }: AnalyticsProviderProps) {
  const GA_TRACKING_ID = process.env.NEXT_PUBLIC_GA_TRACKING_ID;
  const isProduction = process.env.NODE_ENV === 'production';

  useEffect(() => {
    // Initialize Google Analytics with consent mode
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('consent', 'default', {
        analytics_storage: 'denied',
        ad_storage: 'denied',
        wait_for_update: 500,
      });
      
      window.gtag('config', GA_TRACKING_ID, {
        page_title: document.title,
        page_location: window.location.href,
        send_page_view: false, // We'll send this manually
      });
    }
  }, [GA_TRACKING_ID]);

  if (!GA_TRACKING_ID || !isProduction) {
    return <>{children}</>;
  }

  return (
    <>
      {/* Google Analytics */}
      <Script
        strategy="afterInteractive"
        src={`https://www.googletagmanager.com/gtag/js?id=${GA_TRACKING_ID}`}
      />
      <Script
        id="google-analytics"
        strategy="afterInteractive"
        dangerouslySetInnerHTML={{
          __html: `
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
          `,
        }}
      />
      {children}
    </>
  );
}

// Analytics utility functions
export const analytics = {
  // Track page views
  pageView: (url: string, title?: string) => {
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', 'page_view', {
        page_title: title || document.title,
        page_location: url,
      });
    }
  },

  // Track custom events
  event: (eventName: string, parameters: Record<string, unknown> = {}) => {
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', eventName, parameters);
    }
  },

  // Track user interactions
  trackClick: (elementName: string, location?: string) => {
    analytics.event('click', {
      element_name: elementName,
      location: location || 'unknown',
    });
  },

  // Track form submissions
  trackFormSubmit: (formName: string, success: boolean = true) => {
    analytics.event('form_submit', {
      form_name: formName,
      success,
    });
  },

  // Track social media connections
  trackSocialConnect: (platform: string, success: boolean = true) => {
    analytics.event('social_connect', {
      platform,
      success,
    });
  },

  // Track content publishing
  trackContentPublish: (platform: string, contentType: string) => {
    analytics.event('content_publish', {
      platform,
      content_type: contentType,
    });
  },

  // Track user engagement
  trackEngagement: (action: string, category: string, value?: number) => {
    analytics.event('engagement', {
      action,
      category,
      value,
    });
  },
};