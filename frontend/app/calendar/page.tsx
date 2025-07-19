import { DashboardLayout } from "@/components/dashboard/layout";
import { CalendarView } from "@/components/calendar/calendar-view";

export default function CalendarPage() {
  return (
    <DashboardLayout>
      <CalendarView />
    </DashboardLayout>
  );
}