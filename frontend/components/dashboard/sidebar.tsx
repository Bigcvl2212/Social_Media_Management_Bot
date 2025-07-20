"use client";

import { Fragment } from "react";
import { Dialog, Transition } from "@headlessui/react";
import { XMarkIcon } from "@heroicons/react/24/outline";
import {
  HomeIcon,
  CalendarIcon,
  PhotoIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  UserGroupIcon,
  LinkIcon,
} from "@heroicons/react/24/outline";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { clsx } from "clsx";

const navigation = [
  { name: "Dashboard", href: "/", icon: HomeIcon },
  { name: "Content", href: "/content", icon: PhotoIcon },
  { name: "Calendar", href: "/calendar", icon: CalendarIcon },
  { name: "Social Accounts", href: "/accounts", icon: LinkIcon },
  { name: "Analytics", href: "/analytics", icon: ChartBarIcon },
  { name: "Team", href: "/team", icon: UserGroupIcon },
  { name: "Settings", href: "/settings", icon: Cog6ToothIcon },
];

interface SidebarProps {
  open: boolean;
  setOpen: (open: boolean) => void;
}

export function Sidebar({ open, setOpen }: SidebarProps) {
  const pathname = usePathname();

  return (
    <>
      {/* Mobile sidebar */}
      <Transition.Root show={open} as={Fragment}>
        <Dialog as="div" className="relative z-50 lg:hidden" onClose={setOpen}>
          <Transition.Child
            as={Fragment}
            enter="transition-opacity ease-linear duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="transition-opacity ease-linear duration-300"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-black/60 backdrop-blur-sm" />
          </Transition.Child>

          <div className="fixed inset-0 flex">
            <Transition.Child
              as={Fragment}
              enter="transition ease-in-out duration-300 transform"
              enterFrom="-translate-x-full"
              enterTo="translate-x-0"
              leave="transition ease-in-out duration-300 transform"
              leaveFrom="translate-x-0"
              leaveTo="-translate-x-full"
            >
              <Dialog.Panel className="relative mr-16 flex w-full max-w-xs flex-1">
                <Transition.Child
                  as={Fragment}
                  enter="ease-in-out duration-300"
                  enterFrom="opacity-0"
                  enterTo="opacity-100"
                  leave="ease-in-out duration-300"
                  leaveFrom="opacity-100"
                  leaveTo="opacity-0"
                >
                  <div className="absolute left-full top-0 flex w-16 justify-center pt-5">
                    <button
                      type="button"
                      className="-m-2.5 p-2.5 rounded-full glass hover:bg-white/20 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-gray-800"
                      onClick={() => setOpen(false)}
                      aria-label="Close navigation menu"
                    >
                      <XMarkIcon className="h-6 w-6 text-white" aria-hidden="true" />
                    </button>
                  </div>
                </Transition.Child>
                <SidebarContent pathname={pathname} />
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </Dialog>
      </Transition.Root>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-72 lg:flex-col">
        <SidebarContent pathname={pathname} />
      </div>
    </>
  );
}

function SidebarContent({ pathname }: { pathname: string }) {
  return (
    <div className="flex grow flex-col gap-y-5 overflow-y-auto glass-strong px-6 pb-4 border-r border-white/10 backdrop-blur-xl">
      <div className="flex h-16 shrink-0 items-center">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
            <span className="text-white font-bold text-sm" aria-hidden="true">S</span>
          </div>
          <h1 className="text-xl font-bold gradient-text">
            SocialBot
          </h1>
        </div>
      </div>
      <nav className="flex flex-1 flex-col" role="navigation" aria-label="Main navigation">
        <ul role="list" className="flex flex-1 flex-col gap-y-7">
          <li>
            <ul role="list" className="-mx-2 space-y-2">
              {navigation.map((item, index) => (
                <li key={item.name} className="animate-slide-in-up" style={{animationDelay: `${index * 50}ms`}}>
                  <Link
                    href={item.href}
                    className={clsx(
                      pathname === item.href
                        ? "bg-gradient-to-r from-blue-500/20 to-purple-500/20 text-blue-300 border-r-2 border-blue-400"
                        : "text-gray-300 hover:text-white hover:bg-white/5",
                      "group flex gap-x-3 rounded-xl p-3 text-sm leading-6 font-semibold transition-all duration-300 interactive-card focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-gray-800"
                    )}
                    aria-current={pathname === item.href ? 'page' : undefined}
                  >
                    <item.icon
                      className={clsx(
                        pathname === item.href
                          ? "text-blue-400"
                          : "text-gray-400 group-hover:text-white",
                        "h-6 w-6 shrink-0 transition-colors duration-300"
                      )}
                      aria-hidden="true"
                    />
                    <span>{item.name}</span>
                  </Link>
                </li>
              ))}
            </ul>
          </li>
          
          {/* Add AI Assistant Section */}
          <li className="mt-auto">
            <div className="glass rounded-xl p-4 border border-white/10" role="region" aria-label="AI Assistant Status">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-green-400 to-blue-500 flex items-center justify-center animate-glow" aria-hidden="true">
                  <span className="text-white font-bold text-xs">AI</span>
                </div>
                <div>
                  <p className="text-sm font-medium text-white">AI Assistant</p>
                  <p className="text-xs text-gray-400">Online & Ready</p>
                </div>
              </div>
            </div>
          </li>
        </ul>
      </nav>
    </div>
  );
}