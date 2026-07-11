"use client";

import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const COLORS = ["#0ea5e9", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"];

export default function AdminInsightsPage() {
  const [health, setHealth] = useState<any>(null);
  const [activation, setActivation] = useState<any>(null);
  const [retention, setRetention] = useState<any>(null);
  const [support, setSupport] = useState<any>(null);
  const [pmf, setPmf] = useState<any>(null);
  const [riskDashboard, setRiskDashboard] = useState<any[]>([]);
  const [anomalies, setAnomalies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [healthRes, activationRes, retentionRes, supportRes, pmfRes, anomalyRes, riskRes] = await Promise.all([
          fetch("/api/v1/admin/insights/health"),
          fetch("/api/v1/admin/insights/activation-trends"),
          fetch("/api/v1/admin/insights/retention-summary"),
          fetch("/api/v1/admin/insights/support-analytics"),
          fetch("/api/v1/admin/insights/pmf"),
          fetch("/api/v1/admin/insights/anomalies"),
          fetch("/api/v1/admin/insights/retention-risk"),
        ]);

        if (healthRes.ok) setHealth(await healthRes.json());
        if (activationRes.ok) setActivation(await activationRes.json());
        if (retentionRes.ok) setRetention(await retentionRes.json());
        if (supportRes.ok) setSupport(await supportRes.json());
        if (pmfRes.ok) setPmf(await pmfRes.json());
        if (anomalyRes.ok) setAnomalies(await anomalyRes.json());
        if (riskRes.ok) setRiskDashboard(await riskRes.json());
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return <div className="p-8 text-sm text-slate-600">Loading Platform Intelligence...</div>;
  }

  return (
    <main className="min-h-screen bg-slate-50 p-4 md:p-8">
      <div className="mx-auto max-w-7xl space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-slate-900">Platform Intelligence</h1>
            <p className="mt-1 text-sm text-slate-600">Operational health, PMF signals, and growth diagnostics.</p>
          </div>
          <div className={`rounded-full px-4 py-1 text-xs font-bold ${health?.status === 'HEALTHY' ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'}`}>
            SYSTEM: {health?.status || 'UNKNOWN'}
          </div>
        </div>

        {anomalies.length > 0 && (
          <div className="rounded-2xl border border-red-200 bg-red-50 p-4 shadow-sm">
            <h2 className="text-sm font-bold text-red-800 uppercase tracking-wide">Operational Anomalies Detected</h2>
            <ul className="mt-3 space-y-2">
              {anomalies.map((a, i) => (
                <li key={i} className="flex items-start gap-3 text-sm text-red-700">
                  <span className="font-bold">[{a.severity}]</span>
                  <span>{a.description}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Card label="Platform DAU" value={health?.daily_active_tenants || 0} />
          <Card label="Workflow Success" value={`${health?.workflow_success_rate_pct || 0}%`} />
          <Card label="Avg Activation" value={`${activation?.avg_completion_pct || 0}%`} />
          <Card label="Conversion Rate" value={`${pmf?.data_summary?.overall_conversion_rate_pct || 0}%`} />
        </section>

        <section className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <Panel title="Retention Cohort Analysis">
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={retention?.cohort_analysis || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="cohort" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="retention_rate_pct" fill="#6366f1" radius={[8, 8, 0, 0]} name="Retention Rate %" />
              </BarChart>
            </ResponsiveContainer>
          </Panel>

          <Panel title="Support Friction Clusters">
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie
                  data={support?.top_issue_clusters || []}
                  dataKey="count"
                  nameKey="category"
                  innerRadius={60}
                  outerRadius={100}
                >
                  {(support?.top_issue_clusters || []).map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Panel>
        </section>

        <section className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <Panel title="PMF Learning: Vertical Success">
            <div className="mt-2 space-y-3">
              {(pmf?.data_summary?.top_verticals || []).map((v: string, i: number) => (
                <div key={v} className="flex items-center justify-between rounded-xl bg-white p-3 border border-slate-100">
                  <span className="text-sm font-medium text-slate-700">{v}</span>
                  <span className="text-xs font-bold text-indigo-600">RANK #{i+1}</span>
                </div>
              ))}
            </div>
          </Panel>

          <Panel title="Success Signals & Uplift">
            <div className="space-y-4 py-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-500">Key Feature Uplift</span>
                <span className="text-xl font-bold text-green-600">+{pmf?.data_summary?.key_feature_uplift || 0}%</span>
              </div>
              <ul className="mt-4 space-y-2">
                {(pmf?.success_signals || []).map((s: string) => (
                  <li key={s} className="text-sm text-slate-600 flex items-center gap-2">
                    <span className="h-1.5 w-1.5 rounded-full bg-green-500" />
                    {s}
                  </li>
                ))}
              </ul>
            </div>
          </Panel>
        </section>

        <section className="grid grid-cols-1 gap-4">
          <Panel title="Retention Risk & Intervention Dashboard">
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="text-xs uppercase text-slate-400 border-b border-slate-100">
                    <th className="pb-3 font-semibold">Business Name</th>
                    <th className="pb-3 font-semibold">Risk Level</th>
                    <th className="pb-3 font-semibold">Trend</th>
                    <th className="pb-3 font-semibold text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {riskDashboard.map((tenant) => (
                    <tr key={tenant.tenant_id} className="hover:bg-slate-50 transition-colors">
                      <td className="py-4 text-sm font-medium text-slate-700">{tenant.business_name}</td>
                      <td className="py-4">
                        <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${
                          tenant.risk_level === 'HIGH' ? 'bg-red-100 text-red-600' : 'bg-amber-100 text-amber-600'
                        }`}>
                          {tenant.risk_level}
                        </span>
                      </td>
                      <td className="py-4 text-sm font-mono text-slate-500">
                        {tenant.engagement_trend > 0 ? '+' : ''}{tenant.engagement_trend * 100}%
                      </td>
                      <td className="py-4 text-right">
                        <button className="text-xs font-bold text-indigo-600 hover:text-indigo-800">
                          Create Success Issue
                        </button>
                      </td>
                    </tr>
                  ))}
                  {riskDashboard.length === 0 && (
                    <tr>
                      <td colSpan={4} className="py-12 text-center text-sm text-slate-400 italic">
                        No high-risk tenants detected in this window.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </Panel>
        </section>
      </div>
    </main>
  );
}

function Card({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
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
