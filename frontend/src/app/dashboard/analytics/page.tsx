"use client";

import { useEffect, useMemo, useState } from "react";
import { authFetch } from "@/lib/api";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type KPI = {
  lead_total: number;
  booked_leads: number;
  appointments_total: number;
  conversations_total: number;
  booking_conversion_pct: number;
  no_show_rate_pct: number;
};

const fallbackKpi: KPI = {
  lead_total: 0,
  booked_leads: 0,
  appointments_total: 0,
  conversations_total: 0,
  booking_conversion_pct: 0,
  no_show_rate_pct: 0,
};

export default function AnalyticsDashboardPage() {
  const [kpi, setKpi] = useState<KPI>(fallbackKpi);
  const [bookingTrends, setBookingTrends] = useState<{ date: string; bookings: number }[]>([]);
  const [pipeline, setPipeline] = useState<{ stage: string; count: number }[]>([]);
  const [retention, setRetention] = useState({ customers_total: 0, repeat_customers: 0, repeat_rate_pct: 0 });
  const [activation, setActivation] = useState<{ onboarding_completion_pct: number; is_activated: bool; bottlenecks: string[] } | null>(null);
  const [conversion, setConversion] = useState<{ current_tier: string; conversion_probability: number } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [kpiRes, trendRes, pipelineRes, retentionRes, activationRes, conversionRes] = await Promise.all([
          authFetch("/api/v1/analytics/kpis"),
          authFetch("/api/v1/analytics/booking-trends?days=30"),
          authFetch("/api/v1/analytics/pipeline"),
          authFetch("/api/v1/analytics/retention"),
          authFetch("/api/v1/analytics/activation"),
          authFetch("/api/v1/analytics/conversion"),
        ]);

        if (kpiRes.ok) setKpi(await kpiRes.json());
        if (trendRes.ok) setBookingTrends(await trendRes.json());
        if (pipelineRes.ok) setPipeline(await pipelineRes.json());
        if (retentionRes.ok) setRetention(await retentionRes.json());
        if (activationRes.ok) setActivation(await activationRes.json());
        if (conversionRes.ok) setConversion(await conversionRes.json());
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const hasData = useMemo(() => kpi.lead_total > 0 || bookingTrends.length > 0, [kpi, bookingTrends]);

  if (loading) {
    return (
      <div className="space-y-6 p-8 animate-pulse">
        <div className="h-10 w-64 bg-slate-200 rounded" />
        <div className="grid grid-cols-3 gap-4">
           {[1,2,3,4,5,6].map(i => <div key={i} className="h-24 bg-white border border-slate-100 rounded-2xl shadow-sm" />)}
        </div>
        <div className="grid grid-cols-2 gap-4">
           <div className="h-64 bg-white border border-slate-100 rounded-2xl shadow-sm" />
           <div className="h-64 bg-white border border-slate-100 rounded-2xl shadow-sm" />
        </div>
      </div>
    );
  }

  if (!hasData) {
    return (
      <div className="m-8 rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
        <h1 className="text-2xl font-semibold text-slate-900">Analytics Dashboard</h1>
        <p className="mt-3 text-slate-600">No analytics events yet. Complete onboarding or run demo seed data.</p>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-amber-50 via-white to-cyan-50 p-4 md:p-8">
      <div className="mx-auto max-w-7xl space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">Revenue Analytics</h1>
          <p className="mt-1 text-sm text-slate-600">Lead quality, conversion, retention, and booking trends.</p>
        </div>

        <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <Card label="Leads" value={kpi.lead_total} />
          <Card label="Booked Leads" value={kpi.booked_leads} />
          <Card label="Appointments" value={kpi.appointments_total} />
          <Card label="Conversations" value={kpi.conversations_total} />
          <Card label="Booking Conversion" value={`${kpi.booking_conversion_pct}%`} />
          <Card label="No-show Rate" value={`${kpi.no_show_rate_pct}%`} />
        </section>

        <section className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <Panel title="Booking Trends (30d)">
            <ResponsiveContainer width="100%" height={260}>
              <AreaChart data={bookingTrends}>
                <defs>
                  <linearGradient id="bookings" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0.1} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" hide />
                <YAxis />
                <Tooltip />
                <Area type="monotone" dataKey="bookings" stroke="#0284c7" fill="url(#bookings)" />
              </AreaChart>
            </ResponsiveContainer>
          </Panel>

          <Panel title="Lead Pipeline">
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={pipeline}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="stage" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#14b8a6" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Panel>
        </section>

        <section className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <Panel title="Onboarding & Activation">
            <div className="space-y-4 py-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-500">Completion Score</span>
                <span className="text-xl font-bold text-slate-900">{activation?.onboarding_completion_pct || 0}%</span>
              </div>
              <div className="h-2 w-full rounded-full bg-slate-100">
                <div 
                  className="h-2 rounded-full bg-cyan-500 transition-all" 
                  style={{ width: `${activation?.onboarding_completion_pct || 0}%` }}
                />
              </div>
              {activation?.bottlenecks && activation.bottlenecks.length > 0 && (
                <div className="mt-4">
                  <p className="text-xs font-semibold uppercase text-slate-400">Remaining Steps</p>
                  <ul className="mt-2 space-y-1">
                    {activation.bottlenecks.map(b => (
                      <li key={b} className="text-sm text-slate-600">• {b.replace("_", " ")}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </Panel>

          <Panel title="Commercial Insights">
            <div className="grid grid-cols-2 gap-4 py-2">
              <Stat label="Current Tier" value={conversion?.current_tier || "free"} />
              <Stat label="Conversion Potential" value={`${(conversion?.conversion_probability || 0) * 100}%`} />
            </div>
            <p className="mt-4 text-xs text-slate-500">
              Potential is calculated based on engagement score and usage patterns.
            </p>
          </Panel>
        </section>

        <section className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <Panel title="Customer Retention">
            <div className="grid grid-cols-3 gap-4 py-2">
              <Stat label="Total Customers" value={retention.customers_total} />
              <Stat label="Repeat" value={retention.repeat_customers} />
              <Stat label="Repeat Rate" value={`${retention.repeat_rate_pct}%`} />
            </div>
          </Panel>

          <Panel title="Conversion Split">
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={[
                    { name: "Booked", value: kpi.booked_leads },
                    { name: "Open/Lost", value: Math.max(kpi.lead_total - kpi.booked_leads, 0) },
                  ]}
                  dataKey="value"
                  innerRadius={40}
                  outerRadius={80}
                  fill="#fb923c"
                />
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Panel>
        </section>
      </div>
    </main>
  );
}

function Card({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm hover:shadow-md transition-shadow">
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-slate-900">{value}</p>
    </div>
  );
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-600">{title}</h2>
      {children}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-xl bg-slate-50 p-3">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="text-xl font-semibold text-slate-900">{value}</p>
    </div>
  );
}
