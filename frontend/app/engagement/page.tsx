"use client";

import { DashboardLayout } from "@/components/dashboard/layout";
import { EngagementDashboard } from "@/components/engagement/engagement-dashboard";

export default function EngagementPage() {
  return (
    <DashboardLayout>
      <EngagementDashboard />
    </DashboardLayout>
  );
}
