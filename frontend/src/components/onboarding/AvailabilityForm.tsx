"use client";

import React from "react";

interface AvailabilityFormProps {
  vertical: string;
  data: any[];
  updateData: (data: any[]) => void;
}

const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

export default function AvailabilityForm({ vertical, data, updateData }: AvailabilityFormProps) {
  // If data is empty, suggest 9-5 for weekdays
  const isDefault = data.length === 0;

  const set9to5 = () => {
    const rules = DAYS.slice(0, 5).map(day => ({
      day_of_week: day,
      start_time: "09:00",
      end_time: "17:00"
    }));
    updateData(rules);
  };

  const setHealthcareHours = () => {
     const rules = DAYS.slice(0, 6).map(day => ({
      day_of_week: day,
      start_time: day === "Saturday" ? "09:00" : "08:00",
      end_time: day === "Saturday" ? "13:00" : "18:00"
    }));
    updateData(rules);
  };

  const removeRule = (idx: number) => {
    updateData(data.filter((_, i) => i !== idx));
  };

  return (
    <div className="space-y-6 w-full max-w-2xl mx-auto">
      <div className="flex gap-4">
        <button 
          onClick={set9to5}
          className="flex-1 p-4 border border-gray-200 rounded-xl hover:bg-indigo-50 hover:border-indigo-200 transition-all text-sm font-medium"
        >
          Standard 9-5 (Mon-Fri)
        </button>
        <button 
          onClick={setHealthcareHours}
          className="flex-1 p-4 border border-gray-200 rounded-xl hover:bg-indigo-50 hover:border-indigo-200 transition-all text-sm font-medium"
        >
          Extended {vertical === 'healthcare' ? 'Clinic' : 'Business'} Hours
        </button>
      </div>

      <div className="bg-slate-50 rounded-xl p-6 border border-slate-100">
        <h3 className="text-sm font-bold text-slate-700 mb-4 uppercase tracking-wider">Active Schedule</h3>
        {data.length === 0 ? (
          <p className="text-slate-400 text-sm italic">No hours set yet. Pick a preset above to start.</p>
        ) : (
          <div className="space-y-2">
            {data.map((rule, idx) => (
              <div key={idx} className="flex items-center justify-between bg-white p-3 rounded-lg border border-slate-100 group">
                <span className="font-medium text-slate-700 w-24">{rule.day_of_week}</span>
                <span className="text-sm text-slate-500">{rule.start_time} - {rule.end_time}</span>
                <button 
                  onClick={() => removeRule(idx)}
                  className="text-slate-300 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-all"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <p className="text-xs text-slate-400 text-center">
        You can refine specific time slots and breaks later in the dashboard.
      </p>
    </div>
  );
}
