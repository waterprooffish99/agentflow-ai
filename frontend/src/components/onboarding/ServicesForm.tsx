"use client";

import React from "react";

interface ServicesFormProps {
  vertical: string;
  data: any[];
  updateData: (data: any[]) => void;
}

const PRESETS: Record<string, string[]> = {
  healthcare: ["General Consultation", "Follow-up Appointment", "X-Ray / Imaging", "Blood Work"],
  legal: ["Initial Consultation", "Document Review", "Case Strategy Session", "Contract Drafting"],
  realestate: ["Property Viewing", "Market Appraisal", "Listing Presentation", "Closing Meeting"],
  beauty: ["Haircut & Style", "Manicure & Pedicure", "Facial Treatment", "Massage Therapy"],
  other: ["Standard Consultation", "Service Call", "General Inquiry"],
};

export default function ServicesForm({ vertical, data, updateData }: ServicesFormProps) {
  const presets = PRESETS[vertical] || PRESETS.other;

  const toggleService = (service: string) => {
    if (data.includes(service)) {
      updateData(data.filter((s) => s !== service));
    } else {
      updateData([...data, service]);
    }
  };

  return (
    <div className="space-y-6 w-full max-w-2xl mx-auto">
      <div>
        <p className="text-sm font-medium text-gray-500 mb-4">
          Recommended services for your <span className="font-bold text-indigo-600 capitalize">{vertical || "business"}</span>
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {presets.map((service) => (
            <button
              key={service}
              onClick={() => toggleService(service)}
              className={`text-left p-4 rounded-xl border-2 transition-all flex justify-between items-center ${
                data.includes(service)
                  ? "border-indigo-600 bg-indigo-50"
                  : "border-gray-100 bg-white hover:border-gray-200"
              }`}
            >
              <span className="font-medium text-gray-900">{service}</span>
              {data.includes(service) && <span className="text-indigo-600 text-lg">✓</span>}
            </button>
          ))}
        </div>
      </div>

      <div className="pt-6 border-t border-gray-100">
        <label className="block text-sm font-medium text-gray-700 mb-2">Or add a custom service</label>
        <div className="flex gap-2">
          <input
            type="text"
            className="flex-1 border border-gray-300 rounded-xl p-3 focus:ring-2 focus:ring-indigo-500 outline-none"
            placeholder="e.g. Premium Consulting"
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                const val = (e.target as HTMLInputElement).value;
                if (val && !data.includes(val)) {
                  updateData([...data, val]);
                  (e.target as HTMLInputElement).value = "";
                }
              }
            }}
          />
          <button className="bg-gray-100 text-gray-600 px-6 rounded-xl font-medium hover:bg-gray-200">
            Add
          </button>
        </div>
      </div>

      {data.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-4">
          {data.map((s) => (
            <div key={s} className="bg-indigo-100 text-indigo-700 px-3 py-1 rounded-full text-sm font-medium flex items-center gap-2">
              {s}
              <button onClick={() => toggleService(s)} className="hover:text-indigo-900">×</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
