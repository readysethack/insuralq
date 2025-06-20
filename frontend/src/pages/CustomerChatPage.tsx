import React, { useState, useRef, useEffect } from "react";
import ClaimForm from "../components/ClaimForm";

interface Message {
  sender: "user" | "bot";
  text: string;
}

const initialBotMsg = {
  sender: "bot",
  text: "Hi! I am your Second Opinion Bot. Please describe your insurance claim or inquiry, and I will guide you through the process.",
};

const mockBotReply = (input: string): string => {
  if (input.toLowerCase().includes("accident")) {
    return "Thank you for reporting an accident. Please provide the date, location, and a brief description of what happened.";
  }
  if (input.toLowerCase().includes("theft")) {
    return "For theft claims, please specify what was stolen, when, and where. I will help you with the next steps.";
  }
  if (input.length < 10) {
    return "Could you please provide more details about your claim or question?";
  }
  return "Thank you for your information. Your claim has been recorded. An investigator will review it soon.";
};

const CustomerChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([initialBotMsg]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    const userMsg: Message = { sender: "user", text: input };
    setMessages((msgs) => [...msgs, userMsg]);
    setInput("");
    setLoading(true);
    setTimeout(() => {
      const botText = mockBotReply(userMsg.text);
      setMessages((msgs) => [...msgs, { sender: "bot", text: botText }]);
      setLoading(false);
    }, 900);
  };

  return (
    <div className="min-h-screen flex flex-col items-center bg-gray-50 dark:bg-gray-900 py-8">
      <div className="w-full max-w-2xl bg-white dark:bg-gray-800 rounded-xl shadow-lg flex flex-col h-[70vh]">
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${
                msg.sender === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`px-4 py-2 rounded-lg max-w-[70%] ${
                  msg.sender === "user"
                    ? "bg-blue-600 text-white"
                    : "bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                } shadow-md`}
              >
                {msg.text}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="px-4 py-2 rounded-lg bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-100 animate-pulse">
                Bot is typing...
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>
        <form
          onSubmit={handleSend}
          className="p-4 border-t border-gray-200 dark:border-gray-700 flex gap-2"
        >
          <input
            type="text"
            className="flex-1 px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Type your claim or question..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
          />
          <button
            type="submit"
            className="px-6 py-2 rounded-lg bg-blue-600 text-white font-bold hover:bg-blue-700 transition disabled:opacity-60"
            disabled={loading || !input.trim()}
          >
            Send
          </button>
        </form>
      </div>
      <ClaimForm />
    </div>
  );
};

export default CustomerChatPage;
