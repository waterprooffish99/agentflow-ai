"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const res = await fetch("/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (res.ok) {
        const data = await res.json();
        // Save token for authenticated requests
        localStorage.setItem("auth_token", data.access_token);
        // Save tenant_id for components that need it (like ChatWidget)
        if (data.user?.tenant_id) {
          localStorage.setItem("tenant_id", data.user.tenant_id);
          document.cookie = `tenant_id=${data.user.tenant_id}; path=/; max-age=86400; SameSite=Lax`;
        }
        // Also set a cookie for RSC/proxy support
        document.cookie = `auth_token=${data.access_token}; path=/; max-age=86400; SameSite=Lax`;
        
        // Redirect based on onboarding status
        // For now, redirect to analytics to be safe
        router.push("/dashboard/analytics");
      } else {
        const err = await res.json();
        alert(err.detail || "Login failed. Please check your credentials.");
      }
    } catch (err) {
      console.error(err);
      alert("An error occurred. Please check your connection and try again.");
    } finally {
      // CRITICAL: This ensures the loading dim state is removed even if the request fails
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
          <h1 className="text-2xl font-bold text-slate-900">Welcome Back</h1>
          <p className="text-slate-500 mt-2">Log in to manage your AI receptionist.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
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
            {loading ? "Logging in..." : "Sign In"}
          </button>
        </form>

        <p className="text-center text-sm text-slate-500 mt-6">
          Don't have an account?{" "}
          <a href="/register" className="text-indigo-600 font-bold hover:underline">
            Create one
          </a>
        </p>
      </div>
    </main>
  );
}
