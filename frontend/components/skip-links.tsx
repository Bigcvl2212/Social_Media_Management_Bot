'use client';

import Link from 'next/link';

export default function SkipLinks() {
  return (
    <div className="sr-only focus-within:not-sr-only">
      <Link
        href="#main-content"
        className="fixed top-0 left-0 z-[9999] bg-indigo-600 text-white px-4 py-2 text-sm font-medium rounded-br-md focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-indigo-600 transform -translate-y-full focus:translate-y-0 transition-transform"
      >
        Skip to main content
      </Link>
      <Link
        href="#main-navigation"
        className="fixed top-0 left-20 z-[9999] bg-indigo-600 text-white px-4 py-2 text-sm font-medium rounded-br-md focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-indigo-600 transform -translate-y-full focus:translate-y-0 transition-transform"
      >
        Skip to navigation
      </Link>
    </div>
  );
}