'use client';

import { useState, useEffect } from 'react';
import { XMarkIcon, ShieldCheckIcon } from '@heroicons/react/24/outline';
import Cookies from 'js-cookie';

interface CookiePreferences {
  necessary: boolean;
  analytics: boolean;
  marketing: boolean;
}

export default function CookieBanner() {
  const [showBanner, setShowBanner] = useState(false);
  const [showPreferences, setShowPreferences] = useState(false);
  const [preferences, setPreferences] = useState<CookiePreferences>({
    necessary: true,
    analytics: false,
    marketing: false,
  });

  useEffect(() => {
    const consent = Cookies.get('cookie-consent');
    if (!consent) {
      setShowBanner(true);
    }
  }, []);

  const handleAcceptAll = () => {
    const allAccepted = {
      necessary: true,
      analytics: true,
      marketing: true,
    };
    Cookies.set('cookie-consent', JSON.stringify(allAccepted), { expires: 365 });
    setShowBanner(false);
    
    // Enable analytics if accepted
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('consent', 'update', {
        analytics_storage: 'granted',
        ad_storage: 'granted',
      });
    }
  };

  const handleAcceptSelected = () => {
    Cookies.set('cookie-consent', JSON.stringify(preferences), { expires: 365 });
    setShowBanner(false);
    setShowPreferences(false);

    // Update consent for analytics
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('consent', 'update', {
        analytics_storage: preferences.analytics ? 'granted' : 'denied',
        ad_storage: preferences.marketing ? 'granted' : 'denied',
      });
    }
  };

  const handleRejectAll = () => {
    const minimal = {
      necessary: true,
      analytics: false,
      marketing: false,
    };
    Cookies.set('cookie-consent', JSON.stringify(minimal), { expires: 365 });
    setShowBanner(false);
  };

  if (!showBanner) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 p-4 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 shadow-lg">
      <div className="max-w-7xl mx-auto">
        {!showPreferences ? (
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-start gap-3 flex-1">
              <ShieldCheckIcon className="h-6 w-6 text-indigo-600 dark:text-indigo-400 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="text-sm font-medium text-gray-900 dark:text-white">
                  We use cookies
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                  We use cookies to enhance your experience, analyze site traffic, and personalize content. 
                  You can manage your preferences or learn more in our{' '}
                  <a 
                    href="/privacy" 
                    className="text-indigo-600 dark:text-indigo-400 hover:underline"
                  >
                    Privacy Policy
                  </a>.
                </p>
              </div>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-2 w-full sm:w-auto">
              <button
                onClick={() => setShowPreferences(true)}
                className="px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
              >
                Manage Preferences
              </button>
              <button
                onClick={handleRejectAll}
                className="px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
              >
                Reject All
              </button>
              <button
                onClick={handleAcceptAll}
                className="px-3 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-md transition-colors"
              >
                Accept All
              </button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                Cookie Preferences
              </h3>
              <button
                onClick={() => setShowPreferences(false)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <XMarkIcon className="h-5 w-5" />
              </button>
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 border border-gray-200 dark:border-gray-700 rounded-md">
                <div>
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                    Necessary Cookies
                  </h4>
                  <p className="text-sm text-gray-600 dark:text-gray-300">
                    Required for the website to function properly.
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={preferences.necessary}
                  disabled
                  className="h-4 w-4 text-indigo-600 rounded border-gray-300 opacity-50"
                />
              </div>
              
              <div className="flex items-center justify-between p-3 border border-gray-200 dark:border-gray-700 rounded-md">
                <div>
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                    Analytics Cookies
                  </h4>
                  <p className="text-sm text-gray-600 dark:text-gray-300">
                    Help us understand how you use our website.
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={preferences.analytics}
                  onChange={(e) => setPreferences(prev => ({ ...prev, analytics: e.target.checked }))}
                  className="h-4 w-4 text-indigo-600 rounded border-gray-300 focus:ring-indigo-500"
                />
              </div>
              
              <div className="flex items-center justify-between p-3 border border-gray-200 dark:border-gray-700 rounded-md">
                <div>
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                    Marketing Cookies
                  </h4>
                  <p className="text-sm text-gray-600 dark:text-gray-300">
                    Used to deliver relevant advertisements.
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={preferences.marketing}
                  onChange={(e) => setPreferences(prev => ({ ...prev, marketing: e.target.checked }))}
                  className="h-4 w-4 text-indigo-600 rounded border-gray-300 focus:ring-indigo-500"
                />
              </div>
            </div>
            
            <div className="flex justify-end gap-2">
              <button
                onClick={handleAcceptSelected}
                className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-md transition-colors"
              >
                Save Preferences
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}