"use client";

import { Bars3Icon, BellIcon, MagnifyingGlassIcon, ChevronDownIcon } from "@heroicons/react/24/outline";
import { MoonIcon, SunIcon, UserIcon, Cog6ToothIcon, ArrowRightOnRectangleIcon } from "@heroicons/react/24/solid";
import { useTheme } from "next-themes";
import { useSession, signOut } from "next-auth/react";
import { useState, useEffect } from "react";
import { Menu, Transition } from "@headlessui/react";
import { Fragment } from "react";
import Link from "next/link";

interface HeaderProps {
  setSidebarOpen: (open: boolean) => void;
}

export function Header({ setSidebarOpen }: HeaderProps) {
  const { theme, setTheme } = useTheme();
  const { data: session } = useSession();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return null;
  }

  const userInitials = session?.user?.name
    ? session.user.name
        .split(" ")
        .map((word) => word[0])
        .join("")
        .toUpperCase()
        .slice(0, 2)
    : "U";

  return (
    <div className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 glass-strong border-b border-white/10 px-4 sm:gap-x-6 sm:px-6 lg:px-8">
      <button
        type="button"
        className="-m-2.5 p-2.5 text-gray-300 hover:text-white lg:hidden rounded-lg hover:bg-white/10 transition-all duration-200"
        onClick={() => setSidebarOpen(true)}
      >
        <span className="sr-only">Open sidebar</span>
        <Bars3Icon className="h-6 w-6" aria-hidden="true" />
      </button>

      {/* Separator */}
      <div className="h-6 w-px bg-white/10 lg:hidden" aria-hidden="true" />

      <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
        <form className="relative flex flex-1" action="#" method="GET">
          <label htmlFor="search-field" className="sr-only">
            Search
          </label>
          <MagnifyingGlassIcon
            className="pointer-events-none absolute inset-y-0 left-4 h-full w-5 text-gray-400"
            aria-hidden="true"
          />
          <input
            id="search-field"
            className="block h-full w-full border-0 py-0 pl-12 pr-4 text-white placeholder:text-gray-400 focus:ring-0 sm:text-sm bg-white/5 rounded-xl backdrop-blur-sm border border-white/10 focus:border-blue-400/50 transition-all duration-300"
            placeholder="Search content, accounts, analytics..."
            type="search"
            name="search"
          />
        </form>
        <div className="flex items-center gap-x-4 lg:gap-x-6">
          {/* Theme toggle */}
          <button
            type="button"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            className="-m-2.5 p-2.5 text-gray-400 hover:text-white rounded-lg hover:bg-white/10 transition-all duration-200 interactive-card"
          >
            <span className="sr-only">Toggle theme</span>
            {theme === "dark" ? (
              <SunIcon className="h-6 w-6" aria-hidden="true" />
            ) : (
              <MoonIcon className="h-6 w-6" aria-hidden="true" />
            )}
          </button>

          {/* Notifications */}
          <div className="relative">
            <button
              type="button"
              className="-m-2.5 p-2.5 text-gray-400 hover:text-white rounded-lg hover:bg-white/10 transition-all duration-200 interactive-card"
            >
              <span className="sr-only">View notifications</span>
              <BellIcon className="h-6 w-6" aria-hidden="true" />
              {/* Notification badge */}
              <span className="absolute -top-1 -right-1 h-4 w-4 bg-red-500 rounded-full flex items-center justify-center text-xs font-medium text-white animate-glow">
                3
              </span>
            </button>
          </div>

          {/* Separator */}
          <div className="hidden lg:block lg:h-6 lg:w-px lg:bg-white/10" aria-hidden="true" />

          {/* Profile dropdown */}
          <Menu as="div" className="relative">
            <Menu.Button className="-m-1.5 flex items-center p-1.5 hover:bg-white/10 rounded-xl transition-all duration-200 interactive-card">
              <span className="sr-only">Open user menu</span>
              {session?.user?.image ? (
                <img
                  className="h-8 w-8 rounded-full ring-2 ring-white/20"
                  src={session.user.image}
                  alt="Profile"
                />
              ) : (
                <div className="h-8 w-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center ring-2 ring-white/20">
                  <span className="text-sm font-medium text-white">{userInitials}</span>
                </div>
              )}
              <span className="hidden lg:flex lg:items-center">
                <span className="ml-4 text-sm font-semibold leading-6 text-white" aria-hidden="true">
                  {session?.user?.name || "User"}
                </span>
                <ChevronDownIcon className="ml-2 h-4 w-4 text-gray-400" />
              </span>
            </Menu.Button>
            <Transition
              as={Fragment}
              enter="transition ease-out duration-100"
              enterFrom="transform opacity-0 scale-95"
              enterTo="transform opacity-100 scale-100"
              leave="transition ease-in duration-75"
              leaveFrom="transform opacity-100 scale-100"
              leaveTo="transform opacity-0 scale-95"
            >
              <Menu.Items className="absolute right-0 z-10 mt-2.5 w-56 origin-top-right rounded-md bg-white dark:bg-gray-800 py-2 shadow-lg ring-1 ring-gray-900/5 dark:ring-gray-700 focus:outline-none">
                <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {session?.user?.name}
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
                    {session?.user?.email}
                  </p>
                </div>
                <Menu.Item>
                  {({ active }) => (
                    <Link
                      href="/profile"
                      className={`${
                        active ? "bg-gray-100 dark:bg-gray-700" : ""
                      } flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300`}
                    >
                      <UserIcon className="mr-3 h-4 w-4" />
                      Your Profile
                    </Link>
                  )}
                </Menu.Item>
                <Menu.Item>
                  {({ active }) => (
                    <Link
                      href="/settings"
                      className={`${
                        active ? "bg-gray-100 dark:bg-gray-700" : ""
                      } flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300`}
                    >
                      <Cog6ToothIcon className="mr-3 h-4 w-4" />
                      Settings
                    </Link>
                  )}
                </Menu.Item>
                <div className="border-t border-gray-200 dark:border-gray-700">
                  <Menu.Item>
                    {({ active }) => (
                      <button
                        onClick={() => signOut({ callbackUrl: "/" })}
                        className={`${
                          active ? "bg-gray-100 dark:bg-gray-700" : ""
                        } flex w-full items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300`}
                      >
                        <ArrowRightOnRectangleIcon className="mr-3 h-4 w-4" />
                        Sign out
                      </button>
                    )}
                  </Menu.Item>
                </div>
              </Menu.Items>
            </Transition>
          </Menu>
        </div>
      </div>
    </div>
  );
}