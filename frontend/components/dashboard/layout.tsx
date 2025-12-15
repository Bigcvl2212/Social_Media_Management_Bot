"use client";

import { useState } from "react";
import { Sidebar } from "./sidebar";
import { Header } from "./header";

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="h-screen flex">
      {/* Sidebar */}
      <div id="main-navigation">
        <Sidebar open={sidebarOpen} setOpen={setSidebarOpen} />
      </div>
      
      {/* Main content - add left margin on large screens to account for fixed sidebar */}
      <div className="flex-1 flex flex-col overflow-hidden lg:ml-72">
        <Header setSidebarOpen={setSidebarOpen} />
        
        <main id="main-content" className="flex-1 overflow-y-auto" role="main">
          <div className="p-6 lg:p-8 xl:p-10">
            <div className="animate-fade-in-scale">
              {children}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}