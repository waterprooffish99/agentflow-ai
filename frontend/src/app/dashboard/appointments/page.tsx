"use client";

import React, { useState } from "react";
import AppointmentList from "@/components/dashboard/AppointmentList";
import CalendarView from "@/components/dashboard/CalendarView";

export default function AppointmentsPage() {
  const [view, setView] = useState<"list" | "calendar">("list");

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Appointments</h1>
          <p className="text-sm text-gray-500">Manage your business bookings and availability.</p>
        </div>
        <div className="flex bg-gray-100 p-1 rounded-lg">
          <button
            onClick={() => setView("list")}
            className={`px-4 py-1.5 text-sm font-medium rounded-md transition ${
              view === "list" ? "bg-white shadow-sm text-gray-900" : "text-gray-500 hover:text-gray-700"
            }`}
          >
            List
          </button>
          <button
            onClick={() => setView("calendar")}
            className={`px-4 py-1.5 text-sm font-medium rounded-md transition ${
              view === "calendar" ? "bg-white shadow-sm text-gray-900" : "text-gray-500 hover:text-gray-700"
            }`}
          >
            Calendar
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 min-h-[600px]">
        {view === "list" ? <AppointmentList /> : <CalendarView />}
      </div>
    </div>
  );
}
