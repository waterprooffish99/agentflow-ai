"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { 
  Users, 
  Calendar, 
  PieChart,
  LogOut
} from "lucide-react";
import ChatWidget from "@/components/chat/ChatWidget";
import { useState } from "react";
import { authFetch } from "@/lib/api";

const NAV_ITEMS = [
  { href: "/dashboard/analytics", label: "Analytics", icon: PieChart },
  { href: "/dashboard/customers", label: "Customers", icon: Users },
  { href: "/dashboard/appointments", label: "Appointments", icon: Calendar },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const [tenantId, setTenantId] = useState<string | null>(null);

  // Auth Protection: Check for token on mount
  useEffect(() => {
    const getCookie = (name: string) => {
      const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
      if (match) return match[2];
      return null;
    };

    const token = localStorage.getItem("auth_token") || getCookie("auth_token");
    if (!token) {
      router.push("/login");
      return;
    }

    // Load tenant ID from localStorage, cookie or fetch if missing
    const localTenantId = localStorage.getItem("tenant_id") || getCookie("tenant_id");
    if (localTenantId) {
      setTenantId(localTenantId);
    } else {
      // Fallback: Fetch user info if tenant_id is missing
      const fetchUserInfo = async () => {
        try {
          const res = await authFetch("/api/v1/auth/me");
          if (res.ok) {
            const user = await res.json();
            if (user.tenant_id) {
              localStorage.setItem("tenant_id", user.tenant_id);
              setTenantId(user.tenant_id);
            }
          }
        } catch (err) {
          console.error("Failed to fetch user info:", err);
        }
      };
      fetchUserInfo();
    }
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem("auth_token");
    localStorage.removeItem("tenant_id");
    document.cookie = "auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
    document.cookie = "tenant_id=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
    router.push("/login");
  };

  return (
    <div className="flex h-screen bg-gray-50">
...
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-6">
          <h1 className="text-xl font-bold text-indigo-600">AgentFlow AI</h1>
        </div>
        
        <nav className="flex-1 px-4 space-y-1 mt-4">
          {NAV_ITEMS.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center space-x-3 px-4 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  isActive 
                    ? "bg-indigo-50 text-indigo-600" 
                    : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                }`}
              >
                <item.icon className={`w-5 h-5 ${isActive ? "text-indigo-600" : "text-gray-400"}`} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-gray-100">
          <button 
            onClick={handleLogout}
            className="w-full flex items-center space-x-3 px-4 py-2.5 rounded-xl text-sm font-medium text-gray-600 hover:bg-red-50 hover:text-red-600 transition-all"
          >
            <LogOut className="w-5 h-5" />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto p-8">
        <div className="max-w-7xl mx-auto">
          {children}
        </div>
      </main>

      {/* Test AI Chat Widget */}
      {tenantId && (
        <ChatWidget 
          tenantId={tenantId} 
          initialGreeting="Hi! I'm your AI assistant. How can I help you today?" 
        />
      )}
    </div>
  );
}
