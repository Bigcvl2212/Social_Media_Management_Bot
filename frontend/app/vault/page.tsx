"use client";

import { DashboardLayout } from "@/components/dashboard/layout";
import { VaultDashboard } from "@/components/vault/vault-dashboard";

export default function VaultPage() {
  return (
    <DashboardLayout>
      <VaultDashboard />
    </DashboardLayout>
  );
}
