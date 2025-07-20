/**
 * Language Switcher Component
 * Provides a dropdown to select the interface language
 */

import { Fragment } from 'react';
import { Menu, Transition } from '@headlessui/react';
import { ChevronDownIcon, LanguageIcon } from '@heroicons/react/24/outline';
import { useI18n } from '@/lib/i18n';
import { clsx } from 'clsx';

interface LanguageSwitcherProps {
  className?: string;
  compact?: boolean;
}

export function LanguageSwitcher({ className, compact = false }: LanguageSwitcherProps) {
  const { t, currentLanguage, changeLanguage, availableLanguages } = useI18n('common');

  const currentLang = availableLanguages.find(lang => lang.code === currentLanguage);

  return (
    <Menu as="div" className={clsx("relative inline-block text-left", className)}>
      <div>
        <Menu.Button className={clsx(
          "inline-flex w-full justify-center gap-x-1.5 rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50",
          "dark:bg-gray-800 dark:text-white dark:ring-gray-600 dark:hover:bg-gray-700",
          compact && "px-2 py-1"
        )}>
          <LanguageIcon className="h-5 w-5" aria-hidden="true" />
          {!compact && (
            <>
              <span className="ml-2">{currentLang?.flag}</span>
              <span className="hidden sm:inline">{currentLang?.name}</span>
            </>
          )}
          <ChevronDownIcon className="h-5 w-5" aria-hidden="true" />
        </Menu.Button>
      </div>

      <Transition
        as={Fragment}
        enter="transition ease-out duration-100"
        enterFrom="transform opacity-0 scale-95"
        enterTo="transform opacity-100 scale-100"
        leave="transition ease-in duration-75"
        leaveFrom="transform opacity-100 scale-100"
        leaveTo="transform opacity-0 scale-95"
      >
        <Menu.Items className="absolute right-0 z-10 mt-2 w-56 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none dark:bg-gray-800 dark:ring-gray-600">
          <div className="py-1">
            <div className="px-3 py-2 text-xs font-medium text-gray-500 dark:text-gray-400 border-b border-gray-200 dark:border-gray-600">
              {t('language')}
            </div>
            {availableLanguages.map((language) => (
              <Menu.Item key={language.code}>
                {({ active }) => (
                  <button
                    onClick={() => changeLanguage(language.code)}
                    className={clsx(
                      'group flex w-full items-center px-3 py-2 text-sm',
                      active
                        ? 'bg-gray-100 text-gray-900 dark:bg-gray-700 dark:text-white'
                        : 'text-gray-700 dark:text-gray-300',
                      currentLanguage === language.code && 'bg-blue-50 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                    )}
                  >
                    <span className="mr-3 text-lg">{language.flag}</span>
                    <span className="flex-1 text-left">{language.name}</span>
                    {currentLanguage === language.code && (
                      <span className="ml-2 text-blue-600 dark:text-blue-400">✓</span>
                    )}
                  </button>
                )}
              </Menu.Item>
            ))}
          </div>
        </Menu.Items>
      </Transition>
    </Menu>
  );
}