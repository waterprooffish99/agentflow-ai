import React from "react";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
}

export default function ChatMessage({ role, content }: ChatMessageProps) {
  const isUser = role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-2 text-sm ${
          isUser
            ? "bg-indigo-600 text-white rounded-tr-none"
            : "bg-gray-100 text-gray-800 rounded-tl-none border border-gray-200"
        }`}
      >
        {content}
      </div>
    </div>
  );
}
