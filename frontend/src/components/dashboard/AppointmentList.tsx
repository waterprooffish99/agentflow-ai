import React, { useState, useEffect } from "react";
import { authFetch } from "@/lib/api";

export default function AppointmentList() {
  const [appointments, setAppointments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAppointments = async () => {
      try {
        const res = await authFetch("/api/v1/crm/appointments");
        if (res.ok) {
          setAppointments(await res.json());
        }
      } finally {
        setLoading(false);
      }
    };
    fetchAppointments();
  }, []);

  if (loading) {
    return (
      <div className="p-6 space-y-4 animate-pulse">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-12 w-full bg-slate-50 rounded" />
        ))}
      </div>
    );
  }

  return (
    <div className="p-6">
      {appointments.length === 0 && (
        <div className="text-center py-10 text-gray-500">
          No appointments booked yet.
        </div>
      )}
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="border-b border-gray-100">
              <th className="pb-3 font-semibold text-sm text-gray-600">Service</th>
              <th className="pb-3 font-semibold text-sm text-gray-600">Time</th>
              <th className="pb-3 font-semibold text-sm text-gray-600">Status</th>
              <th className="pb-3 font-semibold text-sm text-gray-600 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {appointments.map((app) => (
              <tr key={app.id} className="hover:bg-gray-50 transition">
                <td className="py-4 text-sm text-gray-500">{app.service_type}</td>
                <td className="py-4 text-sm text-gray-500">{new Date(app.start_time).toLocaleString()}</td>
                <td className="py-4 text-sm">
                  <span className={`px-2 py-1 rounded-full text-[10px] font-bold uppercase ${
                    app.status === "confirmed" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
                  }`}>
                    {app.status}
                  </span>
                </td>
                <td className="py-4 text-sm text-right">
                  <button className="text-indigo-600 hover:text-indigo-800 font-medium">Details</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
