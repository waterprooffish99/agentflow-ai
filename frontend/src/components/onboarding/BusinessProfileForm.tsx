"use client";

import React from "react";

interface BusinessProfileFormProps {
  data: any;
  updateData: (data: any) => void;
}

const VERTICALS = [
  { id: "healthcare", label: "Healthcare", description: "Clinics, dentists, physical therapy" },
  { id: "legal", label: "Legal", description: "Law firms, legal consultants" },
  { id: "realestate", label: "Real Estate", description: "Agencies, property management" },
  { id: "beauty", label: "Beauty & Wellness", description: "Salons, spas, gyms" },
  { id: "other", label: "Other / General", description: "Any other business type" },
];

export default function BusinessProfileForm({ data, updateData }: BusinessProfileFormProps) {
  return (
    <div className="space-y-6 w-full max-w-2xl mx-auto">
      <div>
        <label className="block text-sm font-bold text-gray-700 mb-4">Select your business type</label>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {VERTICALS.map((v) => (
            <button
              key={v.id}
              onClick={() => updateData({ vertical: v.id, industry: v.label })}
              className={`text-left p-4 rounded-xl border-2 transition-all ${
                data.vertical === v.id
                  ? "border-indigo-600 bg-indigo-50 shadow-sm"
                  : "border-gray-100 hover:border-gray-200 bg-white"
              }`}
            >
              <p className="font-bold text-gray-900">{v.label}</p>
              <p className="text-xs text-gray-500 mt-1">{v.description}</p>
            </button>
          ))}
        </div>
      </div>

      <div className="pt-4 border-t border-gray-100">
        <label className="block text-sm font-medium text-gray-700 mb-1">Business Description</label>
        <textarea
          value={data.description || ""}
          onChange={(e) => updateData({ description: e.target.value })}
          className="mt-1 block w-full border border-gray-300 rounded-xl shadow-sm p-3 h-24 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
          placeholder="Briefly describe what your business does..."
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Website</label>
          <input
            type="url"
            value={data.website || ""}
            onChange={(e) => updateData({ website: e.target.value })}
            className="mt-1 block w-full border border-gray-300 rounded-xl shadow-sm p-3 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
            placeholder="https://..."
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
          <input
            type="tel"
            value={data.phone || ""}
            onChange={(e) => updateData({ phone: e.target.value })}
            className="mt-1 block w-full border border-gray-300 rounded-xl shadow-sm p-3 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
            placeholder="+1..."
          />
        </div>
      </div>
    </div>
  );
}
