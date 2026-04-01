"use client";

import { DashboardLayout } from "@/components/dashboard/layout";
import { GrowthSpyDashboard } from "@/components/growth/growth-spy-dashboard";

export default function GrowthPage() {
  return (
    <DashboardLayout>
      <GrowthSpyDashboard />
    </DashboardLayout>
  );
}
