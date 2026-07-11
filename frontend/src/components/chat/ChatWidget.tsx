"use client";

import React, { useState, useEffect, useRef } from "react";
import ChatMessage from "./ChatMessage";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface ChatWidgetProps {
  tenantId: string;
  initialGreeting?: string;
}

export default function ChatWidget({ tenantId, initialGreeting }: ChatWidgetProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleOpen = async () => {
    console.log("Opening chat for tenant:", tenantId);
    setIsOpen(true);
    if (!conversationId) {
      setIsTyping(true);
      try {
        const token = typeof window !== "undefined" ? localStorage.getItem("auth_token") : null;
        const res = await fetch("/api/v1/chat/start", {
          method: "POST",
          headers: { 
            "Content-Type": "application/json",
            ...(token ? { "Authorization": `Bearer ${token}` } : {})
          },
          body: JSON.stringify({ tenant_id: tenantId }),
        });
        
        if (!res.ok) {
           let errorMessage = "Failed to start conversation";
           try {
               const error = await res.json();
               errorMessage = error.detail || errorMessage;
           } catch (e) {
               console.error("Non-JSON error response on start:", e);
               errorMessage = "AI initialization failed. Service unavailable.";
           }
           throw new Error(errorMessage);
        }
        
        const data = await res.json();
        console.log("Conversation started:", data.conversation_id);
        setConversationId(data.conversation_id);
        
        if (initialGreeting) {
          setMessages([{ role: "assistant", content: initialGreeting }]);
        }
      } catch (error: any) {
        console.error("Failed to start chat:", error);
        setMessages([{ role: "assistant", content: error.message || "Error connecting to AI. Please refresh and try again." }]);
      } finally {
        setIsTyping(false);
      }
    }
  };

  const handleSend = async () => {
    console.log("Attempting to send message. ConversationID:", conversationId);
    if (!inputValue.trim()) return;
    
    if (!conversationId) {
        console.warn("No conversation ID found. Re-initializing...");
        await handleOpen();
        if (!conversationId) return;
    }

    const userMessage: Message = { role: "user", content: inputValue };
    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsTyping(true);

    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("auth_token") : null;
      const res = await fetch("/api/v1/chat/message", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          ...(token ? { "Authorization": `Bearer ${token}` } : {})
        },
        body: JSON.stringify({
          conversation_id: conversationId,
          tenant_id: tenantId,
          content: userMessage.content,
        }),
      });
      
      if (!res.ok) {
          let errorMessage = "Failed to send message";
          try {
              const error = await res.json();
              errorMessage = error.detail || errorMessage;
          } catch (e) {
              console.error("Non-JSON error response:", e);
              errorMessage = "AI service is currently unavailable. Please check backend logs.";
          }
          throw new Error(errorMessage);
      }
      
      const acceptedData = await res.json();
      const taskId = acceptedData.task_id;
      
      // Poll for the result
      let attempts = 0;
      const maxAttempts = 60; // 60 seconds max
      let pollSuccess = false;
      let assistantMessage = "Sorry, I encountered an error. Please try again.";
      
      while (attempts < maxAttempts) {
        await new Promise((resolve) => setTimeout(resolve, 1000));
        const statusRes = await fetch(`/api/v1/chat/task/${taskId}`, {
          headers: token ? { "Authorization": `Bearer ${token}` } : {}
        });
        if (!statusRes.ok) {
          throw new Error("Failed to check message status");
        }
        const statusData = await statusRes.json();
        if (statusData.status === "SUCCESS") {
          assistantMessage = statusData.result.content;
          pollSuccess = true;
          break;
        } else if (statusData.status === "FAILURE") {
          throw new Error(statusData.result || "AI processing failed");
        }
        attempts++;
      }
      
      if (!pollSuccess) {
        throw new Error("AI response timeout. Please try again.");
      }
      
      setMessages((prev) => [...prev, { role: "assistant", content: assistantMessage }]);
    } catch (error: any) {
      console.error("Failed to send message:", error);
      setMessages((prev) => [...prev, { role: "assistant", content: error.message || "Sorry, I encountered an error. Please try again." }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
      {isOpen ? (
        <div className="bg-white w-[380px] h-[550px] rounded-2xl shadow-2xl border border-gray-100 flex flex-col overflow-hidden animate-in fade-in slide-in-from-bottom-4">
          {/* Header */}
          <div className="bg-indigo-600 p-4 text-white flex justify-between items-center">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center font-bold">
                AI
              </div>
              <div>
                <div className="text-sm font-semibold">Assistant</div>
                <div className="text-[10px] opacity-80 flex items-center">
                  <span className="w-1.5 h-1.5 bg-green-400 rounded-full mr-1"></span>
                  Online
                </div>
              </div>
            </div>
            <button onClick={() => setIsOpen(false)} className="opacity-70 hover:opacity-100">
              ✕
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-2">
            {messages.length === 0 && !isTyping && (
              <div className="text-center text-gray-400 text-xs mt-10">
                Type a message to start chatting...
              </div>
            )}
            {messages.map((msg, i) => (
              <ChatMessage key={i} {...msg} />
            ))}
            {isTyping && (
              <div className="flex justify-start mb-4">
                <div className="bg-gray-100 rounded-2xl rounded-tl-none px-4 py-2 flex space-x-1">
                  <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:0.2s]"></div>
                  <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:0.4s]"></div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-4 border-t border-gray-100 bg-gray-50 flex space-x-2">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSend()}
              placeholder="Type your message..."
              className="flex-1 bg-white border border-gray-200 rounded-full px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <button
              onClick={handleSend}
              disabled={!inputValue.trim()}
              className="w-10 h-10 bg-indigo-600 text-white rounded-full flex items-center justify-center hover:bg-indigo-700 disabled:opacity-50 transition shadow-sm"
            >
              ➔
            </button>
          </div>
        </div>
      ) : (
        <button
          onClick={handleOpen}
          className="w-14 h-14 bg-indigo-600 text-white rounded-full flex items-center justify-center shadow-xl hover:bg-indigo-700 hover:scale-105 transition-all duration-300 animate-in zoom-in"
        >
          <span className="text-2xl">💬</span>
        </button>
      )}
    </div>
  );
}
