"use client";

import React from "react";

interface FAQFormProps {
  vertical: string;
  data: any[];
  updateData: (data: any[]) => void;
}

const VERTICAL_FAQS: Record<string, { q: string, a: string }[]> = {
  healthcare: [
    { q: "Do you take insurance?", a: "We accept most major insurance plans. Please bring your card to your visit." },
    { q: "What should I bring to my first appointment?", a: "Please bring a photo ID and your insurance card." }
  ],
  legal: [
    { q: "What is your hourly rate?", a: "Rates vary by attorney and case complexity. We will discuss this in our initial consultation." },
    { q: "Do you offer free consultations?", a: "Yes, we offer a free 15-minute initial case review." }
  ],
  realestate: [
    { q: "How long does a viewing take?", a: "Typical property viewings last between 20 and 45 minutes." },
    { q: "Can I book a same-day viewing?", a: "We usually require at least 24 hours notice for property viewings." }
  ],
  beauty: [
    { q: "What is your cancellation policy?", a: "We require 24 hours notice for cancellations to avoid a fee." },
    { q: "Do you accept walk-ins?", a: "We prefer appointments but will take walk-ins if a stylist is available." }
  ],
};

export default function FAQForm({ vertical, data, updateData }: FAQFormProps) {
  const [newQ, setNewQ] = React.useState("");
  const [newA, setNewA] = React.useState("");

  const loadPresets = () => {
    const presets = VERTICAL_FAQS[vertical] || [];
    updateData([...data, ...presets]);
  };

  const addCustom = () => {
    if (newQ && newA) {
      updateData([...data, { q: newQ, a: newA }]);
      setNewQ("");
      setNewA("");
    }
  };

  return (
    <div className="space-y-6 w-full max-w-2xl mx-auto">
      <div className="flex justify-between items-center">
        <p className="text-sm text-gray-500 italic">
          Help your AI agent answer common questions.
        </p>
        <button 
          onClick={loadPresets}
          className="text-xs font-bold text-indigo-600 hover:text-indigo-800 uppercase tracking-tight bg-indigo-50 px-3 py-1.5 rounded-lg border border-indigo-100 transition-all"
        >
          + Load {vertical || ''} Presets
        </button>
      </div>

      <div className="space-y-4">
        {data.length === 0 && (
          <div className="text-center py-12 bg-slate-50 rounded-xl border border-dashed border-slate-200">
            <p className="text-slate-400 text-sm">Your knowledge base is empty.</p>
          </div>
        )}
        {data.map((faq, idx) => (
          <div key={idx} className="p-4 bg-white border border-gray-100 rounded-xl shadow-sm space-y-2 group relative">
            <p className="font-bold text-gray-900 text-sm">Q: {faq.q}</p>
            <p className="text-gray-600 text-sm">A: {faq.a}</p>
            <button 
              onClick={() => updateData(data.filter((_, i) => i !== idx))}
              className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 text-red-400 hover:text-red-600 transition-all"
            >
              ×
            </button>
          </div>
        ))}
      </div>

      <div className="pt-4 border-t border-gray-100">
        <div className="bg-gray-50 p-4 rounded-xl space-y-3">
          <input 
            type="text" 
            placeholder="Question" 
            value={newQ}
            onChange={(e) => setNewQ(e.target.value)}
            className="w-full p-2 text-sm border border-gray-300 rounded-lg outline-none focus:ring-1 focus:ring-indigo-500"
          />
          <textarea 
            placeholder="Answer" 
            value={newA}
            onChange={(e) => setNewA(e.target.value)}
            className="w-full p-2 text-sm border border-gray-300 rounded-lg h-20 outline-none focus:ring-1 focus:ring-indigo-500"
          />
          <button 
            onClick={addCustom}
            className="w-full bg-gray-900 text-white text-sm font-bold py-2 rounded-lg hover:bg-black transition-all"
          >
            Add Custom FAQ
          </button>
        </div>
      </div>
    </div>
  );
}
