"use client";

import React, { useState, useEffect } from "react";
import { authFetch } from "@/lib/api";

interface Lead {
  id: string;
  name: string;
  service: string;
  urgency: string;
}

interface Stage {
  id: string;
  name: string;
  leads: Lead[];
}

export default function LeadPipeline() {
  const [stages, setStages] = useState<Stage[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPipeline = async () => {
      try {
        const res = await authFetch("/api/v1/crm/pipeline");
        if (res.ok) {
          setStages(await res.json());
        }
      } finally {
        setLoading(false);
      }
    };
    fetchPipeline();
  }, []);

  if (loading) {
    return (
      <div className="flex space-x-6 p-6 overflow-x-auto min-h-[600px] items-start animate-pulse">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="w-80 flex-shrink-0 bg-gray-50 rounded-xl p-4 h-[500px]" />
        ))}
      </div>
    );
  }

  return (
    <div className="flex space-x-6 p-6 overflow-x-auto min-h-[600px] items-start">
      {stages.length === 0 && (
        <div className="flex-1 text-center py-20 text-gray-500">
          No pipeline stages defined. Please complete onboarding.
        </div>
      )}
      {stages.map((stage) => (
        <div key={stage.id} className="w-80 flex-shrink-0 bg-gray-50 rounded-xl p-4 flex flex-col max-h-full">
          <div className="flex justify-between items-center mb-4 px-2">
            <h3 className="font-bold text-gray-700">{stage.name}</h3>
            <span className="bg-white px-2 py-0.5 rounded-full text-xs font-bold text-gray-500 shadow-sm border border-gray-100">
              {stage.leads.length}
            </span>
          </div>

          <div className="space-y-3 overflow-y-auto">
            {stage.leads.length === 0 && (
              <div className="border-2 border-dashed border-gray-200 rounded-lg p-8 text-center text-gray-400 text-xs italic">
                No leads here
              </div>
            )}
            {stage.leads.map((lead) => (
              <div
                key={lead.id}
                className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:shadow-md hover:border-indigo-100 transition cursor-pointer group"
              >
                <div className="flex justify-between items-start mb-2">
                  <div className="text-sm font-bold text-gray-900 group-hover:text-indigo-600 transition">{lead.name}</div>
                  <span className={`text-[9px] font-bold uppercase px-1.5 py-0.5 rounded ${
                    lead.urgency === "High" ? "bg-red-50 text-red-600" :
                    lead.urgency === "Medium" ? "bg-orange-50 text-orange-600" : "bg-green-50 text-green-600"
                  }`}>
                    {lead.urgency}
                  </span>
                </div>
                <div className="text-xs text-gray-500 mb-3">{lead.service}</div>
                <div className="flex items-center space-x-2 pt-3 border-t border-gray-50">
                  <div className="w-5 h-5 rounded-full bg-indigo-100 flex items-center justify-center text-[10px] text-indigo-600 font-bold">
                    AI
                  </div>
                  <div className="text-[10px] text-gray-400">Qualified 2h ago</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
