"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";

export default function RegisterPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    business_name: "",
    email: "",
    password: "",
    full_name: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const res = await fetch("/api/v1/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (res.ok) {
        const data = await res.json();
        // Save token for onboarding
        localStorage.setItem("auth_token", data.access_token);
        if (data.tenant_id) {
          localStorage.setItem("tenant_id", data.tenant_id);
          document.cookie = `tenant_id=${data.tenant_id}; path=/; max-age=86400; SameSite=Lax`;
        }
        document.cookie = `auth_token=${data.access_token}; path=/; max-age=86400; SameSite=Lax`;
        router.push("/onboarding/profile");
      } else {
        const err = await res.json();
        alert(err.detail || "Registration failed");
      }
    } catch (err) {
      console.error(err);
      alert("An error occurred. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl border border-slate-100 p-8">
        <div className="text-center mb-8">
          <div className="w-12 h-12 bg-indigo-600 rounded-xl mx-auto flex items-center justify-center mb-4 shadow-lg shadow-indigo-200">
            <span className="text-white text-2xl font-bold">A</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900">Get Started with AgentFlow</h1>
          <p className="text-slate-500 mt-2">Set up your AI receptionist in minutes.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Business Name</label>
            <input
              type="text"
              required
              className="w-full border border-slate-200 rounded-xl p-3 focus:ring-2 focus:ring-indigo-500 outline-none transition-all"
              placeholder="Luxe Aesthetics"
              value={formData.business_name}
              onChange={(e) => setFormData({ ...formData, business_name: e.target.value })}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Full Name</label>
            <input
              type="text"
              required
              className="w-full border border-slate-200 rounded-xl p-3 focus:ring-2 focus:ring-indigo-500 outline-none transition-all"
              placeholder="Jane Doe"
              value={formData.full_name}
              onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Email Address</label>
            <input
              type="email"
              required
              className="w-full border border-slate-200 rounded-xl p-3 focus:ring-2 focus:ring-indigo-500 outline-none transition-all"
              placeholder="jane@example.com"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
            <input
              type="password"
              required
              minLength={8}
              className="w-full border border-slate-200 rounded-xl p-3 focus:ring-2 focus:ring-indigo-500 outline-none transition-all"
              placeholder="••••••••"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 text-white rounded-xl py-3 font-bold hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-100 disabled:opacity-50 mt-4"
          >
            {loading ? "Creating Account..." : "Create My AI Agent"}
          </button>
        </form>

        <p className="text-center text-xs text-slate-400 mt-6 px-4">
          By signing up, you agree to our Terms of Service and Privacy Policy.
        </p>
      </div>
    </main>
  );
}
