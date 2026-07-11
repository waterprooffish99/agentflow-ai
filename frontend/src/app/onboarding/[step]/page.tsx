"use client";

import React, { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import BusinessProfileForm from "@/components/onboarding/BusinessProfileForm";
import AIConfigForm from "@/components/onboarding/AIConfigForm";
import ServicesForm from "@/components/onboarding/ServicesForm";
import AvailabilityForm from "@/components/onboarding/AvailabilityForm";
import FAQForm from "@/components/onboarding/FAQForm";
import { authFetch } from "@/lib/api";

const STEPS = [
  { id: "profile", title: "Business Profile", description: "Tell us about your business" },
  { id: "services", title: "Services", description: "What services do you offer?" },
  { id: "availability", title: "Availability", description: "When are you open for bookings?" },
  { id: "faqs", title: "Knowledge Base", description: "Common questions and answers" },
  { id: "ai-config", title: "AI Agent", description: "Configure your AI assistant" },
];

export default function OnboardingStep() {
  const params = useParams();
  const router = useRouter();
  const stepId = params.step as string;
  const currentStepIndex = STEPS.findIndex((s) => s.id === stepId);
  const currentStep = STEPS[currentStepIndex] || STEPS[0];

  // Auth Protection: Check for token on mount and redirect if missing
  React.useEffect(() => {
    const token = localStorage.getItem("auth_token");
    if (!token) {
      router.push("/register");
    }
  }, [router]);

  // State to hold onboarding data across steps
  const [onboardingData, setOnboardingData] = useState({
    profile: { vertical: "other" },
    services: [],
    availability: [],
    faqs: [],
    "ai-config": { personality: "professional", tools: { booking: true, qualification: true } },
  });

  const updateData = (step: string, data: any) => {
    setOnboardingData((prev) => ({
      ...prev,
      [step]: Array.isArray(data) ? data : { ...prev[step as keyof typeof prev], ...data },
    }));
  };

  const handleNext = async () => {
    let data = onboardingData[stepId as keyof typeof onboardingData];
    
    // Safety Fallback for AI Config
    if (stepId === "ai-config" && !data) {
        data = { personality: "professional", tools: { booking: true, qualification: true } };
    }

    console.log(`Saving ${stepId} data:`, data);

    try {
      let endpoint = "";
      let payload = data;

      switch (stepId) {
        case "profile":
          endpoint = "/api/v1/onboarding/business-profile";
          break;
        case "services":
          for (const s of (data as any[])) {
            await authFetch("/api/v1/onboarding/services", {
              method: "POST",
              body: JSON.stringify({ 
                name: s, 
                duration_minutes: 30,
                price: 0,
                is_active: true
              })
            });
          }
          break;
        case "availability":
          for (const rule of (data as any[])) {
             await authFetch("/api/v1/onboarding/availability", {
              method: "POST",
              body: JSON.stringify({
                ...rule,
                is_available: true
              })
            });
          }
          break;
        case "faqs":
          for (const faq of (data as any[])) {
             await authFetch("/api/v1/onboarding/faqs", {
              method: "POST",
              body: JSON.stringify({
                question: faq.q,
                answer: faq.a,
                is_active: true
              })
            });
          }
          break;
        case "ai-config":
          endpoint = "/api/v1/onboarding/ai-config";
          const configData = data || { personality: "professional", tools: { booking: true, qualification: true } };
          payload = {
            name: "default",
            personality_traits: { 
              tone: (configData as any).personality,
              custom_instructions: (configData as any).system_prompt 
            },
            temperature: 0.7,
            model_name: "gpt-4",
            tools_enabled: Object.keys((configData as any).tools || {}).filter(k => (configData as any).tools[k])
          };
          break;
      }

      if (endpoint) {
        const res = await authFetch(endpoint, {
          method: "POST",
          body: JSON.stringify(payload),
        });
        if (!res.ok) {
          const errorData = await res.json();
          throw new Error(errorData.detail || `Failed to save ${stepId}`);
        }
      }

      if (currentStepIndex < STEPS.length - 1) {
        router.push(`/onboarding/${STEPS[currentStepIndex + 1].id}`);
      } else {
        router.push("/dashboard/analytics");
      }
    } catch (err) {
      console.error(err);
      alert(err instanceof Error ? err.message : "Error saving progress. Please try again.");
    }
  };

  const handleBack = () => {
    if (currentStepIndex > 0) {
      router.push(`/onboarding/${STEPS[currentStepIndex - 1].id}`);
    }
  };

  const renderStepForm = () => {
    const vertical = (onboardingData.profile as any).vertical || "other";
    
    switch (stepId) {
      case "profile":
        return <BusinessProfileForm data={onboardingData.profile} updateData={(d) => updateData("profile", d)} />;
      case "services":
        return <ServicesForm vertical={vertical} data={onboardingData.services} updateData={(d) => updateData("services", d)} />;
      case "availability":
        return <AvailabilityForm vertical={vertical} data={onboardingData.availability} updateData={(d) => updateData("availability", d)} />;
      case "faqs":
        return <FAQForm vertical={vertical} data={onboardingData.faqs} updateData={(d) => updateData("faqs", d)} />;
      case "ai-config":
        return <AIConfigForm data={onboardingData["ai-config"]} updateData={(d) => updateData("ai-config", d)} />;
      default:
        return <div>Unknown step</div>;
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Stepper Header */}
      <div className="flex justify-between items-center mb-12">
        {STEPS.map((step, index) => (
          <div key={step.id} className="flex flex-col items-center flex-1 relative">
            <div
              className={`w-10 h-10 rounded-full flex items-center justify-center border-2 z-10 transition-all duration-300 ${
                index <= currentStepIndex
                  ? "bg-indigo-600 border-indigo-600 text-white shadow-md"
                  : "bg-white border-gray-300 text-gray-400"
              }`}
            >
              {index < currentStepIndex ? "✓" : index + 1}
            </div>
            <div className={`mt-2 text-xs font-medium hidden md:block ${
              index <= currentStepIndex ? "text-indigo-600" : "text-gray-400"
            }`}>
              {step.title}
            </div>
            {index < STEPS.length - 1 && (
              <div
                className={`absolute h-0.5 top-5 left-[50%] right-[-50%] z-0 transition-all duration-500 ${
                  index < currentStepIndex ? "bg-indigo-600" : "bg-gray-200"
                }`}
              />
            )}
          </div>
        ))}
      </div>

      {/* Step Content Card */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-8">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900">{currentStep.title}</h2>
          <p className="text-gray-500">{currentStep.description}</p>
        </div>

        <div className="min-h-[300px]">
          {renderStepForm()}
        </div>

        <div className="mt-12 flex justify-between pt-6 border-t border-gray-50">
          <button
            onClick={handleBack}
            disabled={currentStepIndex === 0}
            className="px-8 py-2.5 border border-gray-300 rounded-xl text-gray-700 font-medium hover:bg-gray-50 disabled:opacity-30 transition-all"
          >
            Back
          </button>
          <button
            onClick={handleNext}
            className="px-8 py-2.5 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 shadow-md hover:shadow-lg transition-all"
          >
            {currentStepIndex === STEPS.length - 1 ? "Launch AI Assistant" : "Continue"}
          </button>
        </div>
      </div>
    </div>
  );
}
