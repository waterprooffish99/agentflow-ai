"use client";

import React, { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import CustomerTimeline from "@/components/dashboard/CustomerTimeline";
import { authFetch } from "@/lib/api";

export default function CustomerDetailPage() {
  const params = useParams();
  const customerId = params.id as string;
  const [activeTab, setActiveTab] = useState<"timeline" | "notes" | "bookings">("timeline");
  const [customer, setCustomer] = useState<any>(null);
  const [timeline, setTimeline] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCustomerData = async () => {
      try {
        const [custRes, timelineRes] = await Promise.all([
          authFetch(`/api/v1/crm/customers/${customerId}`),
          authFetch(`/api/v1/crm/customers/${customerId}/timeline`)
        ]);

        if (custRes.ok) setCustomer(await custRes.json());
        if (timelineRes.ok) setTimeline(await timelineRes.json());
      } finally {
        setLoading(false);
      }
    };
    fetchCustomerData();
  }, [customerId]);

  if (loading) return <div className="p-8 text-sm text-slate-600">Loading customer profile...</div>;
  if (!customer) return <div className="p-8 text-sm text-red-600">Customer not found.</div>;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div className="flex items-center space-x-4">
          <div className="w-16 h-16 rounded-full bg-indigo-100 flex items-center justify-center text-2xl font-bold text-indigo-600">
            {customer.name?.[0] || "C"}
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{customer.name}</h1>
            <div className="flex items-center space-x-3 mt-1">
              <span className="text-sm text-gray-500">{customer.email}</span>
              <span className="text-gray-300">•</span>
              <span className="text-sm text-gray-500">{customer.phone}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Left Column: Intelligence Sidebar */}
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 className="font-bold text-gray-900 mb-4 flex items-center">
              <span className="mr-2">🧠</span> AI Intelligence
            </h3>
            <div className="space-y-4">
               <div>
                  <div className="text-[10px] uppercase font-bold text-gray-400 tracking-wider mb-1">Status</div>
                  <div className="text-sm text-gray-700 font-medium">{customer.status}</div>
                </div>
            </div>
          </div>
        </div>

        {/* Right Column: Activity & Tabs */}
        <div className="col-span-2">
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="flex border-b border-gray-100">
              <button
                onClick={() => setActiveTab("timeline")}
                className={`px-6 py-4 text-sm font-bold transition-all border-b-2 ${
                  activeTab === "timeline" ? "border-indigo-600 text-indigo-600" : "border-transparent text-gray-500 hover:text-gray-700"
                }`}
              >
                Activity Timeline
              </button>
            </div>

            <div className="min-h-[400px]">
              {activeTab === "timeline" && <CustomerTimeline activities={timeline} />}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
