"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { SessionProvider } from "next-auth/react";
import { useState } from "react";
import { ThemeProvider } from "./theme-provider";
import { AnalyticsProvider } from "./analytics-provider";
import CookieBanner from "./cookie-banner";
import SkipLinks from "./skip-links";

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient());

  return (
    <SessionProvider>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <AnalyticsProvider>
            <SkipLinks />
            {children}
            <CookieBanner />
          </AnalyticsProvider>
        </ThemeProvider>
      </QueryClientProvider>
    </SessionProvider>
  );
}