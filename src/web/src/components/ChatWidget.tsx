/**
 * ChatWidget component - AI banking assistant chat interface.
 * Provides an embedded chat experience for users to interact with the agent.
 */

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { sendMessageToAgent, checkAgentHealth, AgentError } from "@/services/agentService";
import type { AgentMessage } from "@/types/api";
import { MessageCircle, Send, X, Loader2, AlertCircle } from "lucide-react";

export function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [agentAvailable, setAgentAvailable] = useState<boolean | null>(null);
  const [threadId] = useState<string>(() => `thread-${Date.now()}`);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Check agent health on mount
  useEffect(() => {
    checkAgentHealth().then(setAgentAvailable);
  }, []);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus();
    }
  }, [isOpen]);

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: AgentMessage = {
      id: `msg-${Date.now()}`,
      role: "user",
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);
    setError(null);

    try {
      let assistantContent = "";
      const assistantMessage: AgentMessage = {
        id: `msg-${Date.now()}-assistant`,
        role: "assistant",
        content: "",
        timestamp: new Date(),
      };

      // Add empty assistant message that we'll update
      setMessages((prev) => [...prev, assistantMessage]);

      // Stream the response
      for await (const chunk of sendMessageToAgent(userMessage.content, threadId)) {
        assistantContent += chunk;
        setMessages((prev) => {
          const newMessages = [...prev];
          const lastMessage = newMessages[newMessages.length - 1];
          if (lastMessage.role === "assistant") {
            lastMessage.content = assistantContent;
          }
          return newMessages;
        });
      }
    } catch (err) {
      setError(
        err instanceof AgentError
          ? err.message
          : "Failed to get response from AI assistant"
      );
      // Remove the empty assistant message on error
      setMessages((prev) => prev.filter((m) => m.content !== ""));
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!isOpen) {
    return (
      <div className="fixed bottom-4 right-4 z-50">
        <Button
          onClick={() => setIsOpen(true)}
          size="lg"
          className="h-14 w-14 rounded-full bg-red-600 shadow-lg hover:bg-red-700"
        >
          <MessageCircle className="h-6 w-6" />
          <span className="sr-only">Open chat</span>
        </Button>
      </div>
    );
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 w-96 max-h-[600px] flex flex-col">
      <Card className="flex h-full flex-col border-slate-200 bg-white shadow-2xl">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 border-b border-slate-200 pb-4">
          <CardTitle className="text-lg font-semibold text-slate-900">
            💬 Banking Assistant
          </CardTitle>
          <Button
            onClick={() => setIsOpen(false)}
            variant="ghost"
            size="sm"
            className="h-8 w-8 p-0 text-slate-600 hover:bg-slate-100 hover:text-slate-900"
          >
            <X className="h-4 w-4" />
            <span className="sr-only">Close chat</span>
          </Button>
        </CardHeader>

        <CardContent className="flex-1 overflow-y-auto p-4 space-y-4 min-h-[300px] max-h-[400px]">
          {agentAvailable === false && (
            <div className="flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 p-3">
              <AlertCircle className="mt-0.5 h-5 w-5 flex-shrink-0 text-red-500" />
              <div className="text-sm text-red-700">
                <p className="font-medium">Agent Unavailable</p>
                <p className="mt-1 text-red-600">
                  The AI assistant is currently offline. Please ensure the agent server is running.
                </p>
              </div>
            </div>
          )}

          {messages.length === 0 && agentAvailable !== false && (
            <div className="py-8 text-center text-slate-500">
              <MessageCircle className="mx-auto mb-3 h-12 w-12 text-red-400" />
              <p className="text-sm">Start a conversation!</p>
              <p className="text-xs mt-2">
                Ask about your accounts, transactions, or request a transfer.
              </p>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${
                message.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-3 ${
                  message.role === "user"
                    ? "bg-red-600 text-white"
                    : "border border-slate-200 bg-slate-100 text-slate-900"
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                <p className="text-xs mt-1 opacity-70">
                  {message.timestamp.toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </p>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="rounded-lg border border-slate-200 bg-slate-100 p-3">
                <Loader2 className="h-4 w-4 animate-spin text-slate-500" />
              </div>
            </div>
          )}

          {error && (
            <div className="rounded-lg border border-red-200 bg-red-50 p-3">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          <div ref={messagesEndRef} />
        </CardContent>

        <CardFooter className="border-t border-slate-200 p-4">
          <div className="flex gap-2 w-full">
            <Input
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about your banking..."
              disabled={isLoading || agentAvailable === false}
              className="flex-1 border-slate-300 bg-white text-slate-900 placeholder:text-slate-400"
            />
            <Button
              onClick={handleSendMessage}
              disabled={!input.trim() || isLoading || agentAvailable === false}
              size="icon"
              className="bg-red-600 hover:bg-red-700"
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
              <span className="sr-only">Send message</span>
            </Button>
          </div>
        </CardFooter>
      </Card>
    </div>
  );
}
