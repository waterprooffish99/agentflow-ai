"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { authFetch } from "@/lib/api";

export default function CustomersPage() {
  const [customers, setCustomers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCustomers = async () => {
      try {
        const res = await authFetch("/api/v1/crm/customers");
        if (res.ok) {
          setCustomers(await res.json());
        }
      } finally {
        setLoading(false);
      }
    };
    fetchCustomers();
  }, []);

  if (loading) {
    return (
      <div className="space-y-6 p-8 animate-pulse">
        <div className="h-8 w-48 bg-slate-200 rounded mb-4" />
        <div className="h-4 w-64 bg-slate-100 rounded mb-8" />
        <div className="bg-white rounded-xl border border-slate-100 h-64 shadow-sm" />
      </div>
    );
  }

  if (customers.length === 0) {
    return (
      <div className="m-8 rounded-2xl border border-slate-200 bg-white p-8 shadow-sm text-center">
        <h2 className="text-xl font-semibold text-slate-900">No Customers Found</h2>
        <p className="mt-2 text-slate-500 text-sm">Once your AI starts chatting, customers will appear here.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Customers</h1>
          <p className="text-sm text-gray-500">View and manage your customer relationships.</p>
        </div>
        <div className="flex space-x-3">
          <input
            type="text"
            placeholder="Search customers..."
            className="px-4 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
          />
          <button className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition shadow-sm">
            Add Customer
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-gray-50 border-b border-gray-100">
            <tr>
              <th className="px-6 py-3 font-semibold text-xs text-gray-500 uppercase tracking-wider">Name</th>
              <th className="px-6 py-3 font-semibold text-xs text-gray-500 uppercase tracking-wider">Contact</th>
              <th className="px-6 py-3 font-semibold text-xs text-gray-500 uppercase tracking-wider">Last Interaction</th>
              <th className="px-6 py-3 font-semibold text-xs text-gray-500 uppercase tracking-wider">Status</th>
              <th className="px-6 py-3 font-semibold text-xs text-gray-500 uppercase tracking-wider text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {customers.map((customer) => (
              <tr key={customer.id} className="hover:bg-gray-50 transition cursor-pointer">
                <td className="px-6 py-4">
                  <div className="text-sm font-medium text-gray-900">{customer.name}</div>
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm text-gray-500">{customer.email}</div>
                  <div className="text-[10px] text-gray-400">{customer.phone}</div>
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm text-gray-500">{customer.lastInteraction}</div>
                </td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 rounded-full text-[10px] font-bold uppercase ${
                    customer.status === "booked" ? "bg-green-100 text-green-700" : 
                    customer.status === "qualified" ? "bg-blue-100 text-blue-700" : "bg-gray-100 text-gray-600"
                  }`}>
                    {customer.status}
                  </span>
                </td>
                <td className="px-6 py-4 text-right text-sm">
                  <button className="text-indigo-600 hover:text-indigo-900 font-medium">View</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
