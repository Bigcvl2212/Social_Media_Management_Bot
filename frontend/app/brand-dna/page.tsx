"use client";

import { DashboardLayout } from "@/components/dashboard/layout";
import { BrandDnaDashboard } from "@/components/brand-dna/brand-dna-dashboard";

export default function BrandDnaPage() {
  return (
    <DashboardLayout>
      <BrandDnaDashboard />
    </DashboardLayout>
  );
}
