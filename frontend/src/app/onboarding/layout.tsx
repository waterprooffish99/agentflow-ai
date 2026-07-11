import React from "react";

export default function OnboardingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <header className="bg-white border-b border-gray-200 py-4 px-6">
        <div className="max-w-4xl mx-auto flex justify-between items-center">
          <h1 className="text-xl font-bold text-indigo-600">AgentFlow AI</h1>
          <span className="text-sm text-gray-500">Business Onboarding</span>
        </div>
      </header>
      <main className="flex-1 max-w-4xl mx-auto w-full p-6">
        {children}
      </main>
      <footer className="py-4 text-center text-xs text-gray-400">
        &copy; 2026 AgentFlow AI Platform. All rights reserved.
      </footer>
    </div>
  );
}
