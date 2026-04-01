"use client";

import { DashboardLayout } from "@/components/dashboard/layout";
import { RemixDashboard } from "@/components/remix/remix-dashboard";

export default function RemixPage() {
  return (
    <DashboardLayout>
      <RemixDashboard />
    </DashboardLayout>
  );
}
