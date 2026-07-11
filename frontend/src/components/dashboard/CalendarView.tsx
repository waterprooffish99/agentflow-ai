import React from "react";

export default function CalendarView() {
  return (
    <div className="p-12 flex flex-col items-center justify-center text-gray-400 space-y-4">
      <div className="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center text-2xl">
        📅
      </div>
      <div className="text-center">
        <h3 className="text-lg font-semibold text-gray-900">Interactive Calendar coming soon</h3>
        <p className="text-sm">We are integrating a full calendar view to help you manage schedules better.</p>
      </div>
    </div>
  );
}
