import { generateMetadata as generateSEOMetadata } from '@/lib/seo';
import type { Metadata } from 'next';

export const metadata: Metadata = generateSEOMetadata({
  title: 'Privacy Policy',
  description: 'Privacy policy for Social Media Management Bot - Learn how we protect your data.',
  canonical: '/privacy',
});

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white dark:bg-gray-800 shadow-lg rounded-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
            Privacy Policy
          </h1>
          
          <div className="prose dark:prose-invert max-w-none">
            <p className="text-gray-600 dark:text-gray-300 mb-6">
              Last updated: {new Date().toLocaleDateString()}
            </p>
            
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
                Information We Collect
              </h2>
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                We collect information you provide directly to us, such as when you create an account, 
                connect social media accounts, or contact us for support.
              </p>
              <ul className="list-disc list-inside text-gray-700 dark:text-gray-300 space-y-2">
                <li>Account information (email, username)</li>
                <li>Social media account connections and content</li>
                <li>Usage data and analytics</li>
                <li>Device and browser information</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
                How We Use Your Information
              </h2>
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                We use the information we collect to:
              </p>
              <ul className="list-disc list-inside text-gray-700 dark:text-gray-300 space-y-2">
                <li>Provide and improve our services</li>
                <li>Manage your social media accounts</li>
                <li>Generate analytics and insights</li>
                <li>Send important service notifications</li>
                <li>Ensure security and prevent fraud</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
                Cookies and Tracking
              </h2>
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                We use cookies and similar tracking technologies to enhance your experience. You can 
                manage your cookie preferences through our cookie banner.
              </p>
              <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-md">
                <h3 className="font-medium text-gray-900 dark:text-white mb-2">Cookie Categories:</h3>
                <ul className="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                  <li><strong>Necessary:</strong> Required for the website to function</li>
                  <li><strong>Analytics:</strong> Help us understand how you use our site</li>
                  <li><strong>Marketing:</strong> Used to deliver relevant advertisements</li>
                </ul>
              </div>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
                Your Rights
              </h2>
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                You have the right to:
              </p>
              <ul className="list-disc list-inside text-gray-700 dark:text-gray-300 space-y-2">
                <li>Access your personal data</li>
                <li>Correct inaccurate information</li>
                <li>Delete your account and data</li>
                <li>Withdraw consent for data processing</li>
                <li>Data portability</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
                Contact Us
              </h2>
              <p className="text-gray-700 dark:text-gray-300">
                If you have any questions about this Privacy Policy, please contact us at{' '}
                <a 
                  href="mailto:privacy@socialbot.com" 
                  className="text-indigo-600 dark:text-indigo-400 hover:underline"
                >
                  privacy@socialbot.com
                </a>
              </p>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}