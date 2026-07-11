"use client";

import React from "react";

interface AIConfigFormProps {
  data: any;
  updateData: (data: any) => void;
}

export default function AIConfigForm({ data, updateData }: AIConfigFormProps) {
  return (
    <div className="space-y-6 w-full max-w-lg mx-auto">
      <div>
        <label className="block text-sm font-medium text-gray-700">AI Personality / Tone</label>
        <select
          value={data.personality || "professional"}
          onChange={(e) => updateData({ personality: e.target.value })}
          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
        >
          <option value="professional">Professional & Direct</option>
          <option value="friendly">Friendly & Welcoming</option>
          <option value="empathetic">Empathetic & Supportive</option>
          <option value="humorous">Humorous & Lighthearted</option>
        </select>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">Custom System Instructions</label>
        <textarea
          value={data.system_prompt || ""}
          onChange={(e) => updateData({ system_prompt: e.target.value })}
          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 h-32"
          placeholder="e.g. Always mention our current 20% discount on first consultation..."
        />
      </div>
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">Capabilities</label>
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            checked={data.tools?.booking || false}
            onChange={(e) => updateData({ tools: { ...data.tools, booking: e.target.checked } })}
            className="rounded text-indigo-600"
          />
          <span className="text-sm text-gray-600">Appointment Booking</span>
        </div>
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            checked={data.tools?.qualification || false}
            onChange={(e) => updateData({ tools: { ...data.tools, qualification: e.target.checked } })}
            className="rounded text-indigo-600"
          />
          <span className="text-sm text-gray-600">Lead Qualification</span>
        </div>
      </div>
    </div>
  );
}
