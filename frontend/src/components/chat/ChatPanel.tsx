'use client';

import { useState, useRef, useEffect } from 'react';
import { useChat } from '@/contexts/ChatContext';
import { RotateCcw, X, Send, Loader2 } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function ChatPanel() {
  const { isOpen, closeChat, threadId, setThreadId, startNewChat } = useChat();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(threadId);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen]);

  const sendMessage = async () => {
    const trimmed = input.trim();
    if (!trimmed || loading) return;

    const userMsg: Message = { role: 'user', content: trimmed };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const token = localStorage.getItem('auth_token');
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          message: trimmed,
          conversation_id: conversationId,
        }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Request failed' }));
        setMessages((prev) => [
          ...prev,
          { role: 'assistant', content: `Error: ${err.detail || res.statusText}` },
        ]);
        return;
      }

      const data = await res.json();
      if (data.conversation_id && !conversationId) {
        setConversationId(data.conversation_id);
        setThreadId(data.conversation_id);
      }
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.response },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Connection error. Is the backend running?' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleNewChat = () => {
    startNewChat();
    setMessages([]);
    setConversationId(null);
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Mobile: fullscreen overlay */}
      <div
        className="fixed inset-0 flex flex-col md:hidden"
        style={{ zIndex: 9998, background: 'linear-gradient(135deg, #111827 0%, #000000 50%, #111827 100%)' }}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-700/50 bg-gray-800/50 backdrop-blur-md">
          <h2 className="text-lg font-semibold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-400">
            AI Assistant
          </h2>
          <div className="flex items-center gap-2">
            <button
              onClick={handleNewChat}
              className="p-2 text-gray-400 hover:text-white rounded-md hover:bg-gray-700/50 transition-colors duration-200"
              aria-label="New chat"
              title="New Chat"
            >
              <RotateCcw className="w-5 h-5" />
            </button>
            <button
              onClick={closeChat}
              className="p-2 text-gray-400 hover:text-white rounded-md hover:bg-gray-700/50 transition-colors duration-200"
              aria-label="Close chat"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 min-h-0 overflow-y-auto px-4 py-3 space-y-3">
          {messages.length === 0 && <EmptyState onSelect={setInput} />}
          <MessageList messages={messages} />
          {loading && <TypingIndicator />}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <ChatInput
          inputRef={inputRef}
          input={input}
          setInput={setInput}
          loading={loading}
          onSend={sendMessage}
        />
      </div>

      {/* Desktop: side panel 400px wide, viewport-aware height */}
      <div
        className="hidden md:flex fixed bottom-24 right-6 w-[400px] max-h-[calc(100vh-7rem)] h-[600px] flex-col rounded-2xl shadow-2xl shadow-indigo-500/10 border border-gray-700/50 overflow-hidden backdrop-blur-sm"
        style={{ zIndex: 9998, background: 'linear-gradient(135deg, rgba(17,24,39,0.95) 0%, rgba(0,0,0,0.97) 50%, rgba(17,24,39,0.95) 100%)' }}
      >
        {/* Header */}
        <div className="flex-shrink-0 flex items-center justify-between px-4 py-3 border-b border-gray-700/50 bg-gray-800/50 backdrop-blur-md">
          <h2 className="text-sm font-semibold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-400">
            AI Assistant
          </h2>
          <div className="flex items-center gap-1">
            <button
              onClick={handleNewChat}
              className="p-1.5 text-gray-400 hover:text-white rounded-md hover:bg-gray-700/50 transition-colors duration-200"
              aria-label="New chat"
              title="New Chat"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
            <button
              onClick={closeChat}
              className="p-1.5 text-gray-400 hover:text-white rounded-md hover:bg-gray-700/50 transition-colors duration-200"
              aria-label="Close chat"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 min-h-0 overflow-y-auto px-4 py-3 space-y-3">
          {messages.length === 0 && <EmptyState onSelect={setInput} />}
          <MessageList messages={messages} />
          {loading && <TypingIndicator />}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <ChatInput
          inputRef={inputRef}
          input={input}
          setInput={setInput}
          loading={loading}
          onSend={sendMessage}
        />
      </div>
    </>
  );
}

function EmptyState({ onSelect }: { onSelect: (v: string) => void }) {
  return (
    <div className="text-center mt-8">
      <p className="text-sm text-gray-400">Hi! I can help manage your tasks.</p>
      <div className="mt-4 flex flex-col gap-2 items-center">
        <button
          onClick={() => onSelect('Show me all my tasks')}
          className="text-xs text-indigo-400 hover:text-indigo-300 border border-indigo-500/30 hover:border-indigo-500/60 rounded-full px-4 py-1.5 transition-all duration-200"
        >
          Show my tasks
        </button>
        <button
          onClick={() => onSelect('Add a new task')}
          className="text-xs text-indigo-400 hover:text-indigo-300 border border-indigo-500/30 hover:border-indigo-500/60 rounded-full px-4 py-1.5 transition-all duration-200"
        >
          Add a task
        </button>
      </div>
    </div>
  );
}

function MessageList({ messages }: { messages: Message[] }) {
  return (
    <>
      {messages.map((msg, i) => (
        <div
          key={i}
          className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          <div
            className={`max-w-[80%] rounded-2xl px-3.5 py-2 text-sm whitespace-pre-wrap ${
              msg.role === 'user'
                ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white'
                : 'bg-gray-800/60 text-gray-200 border border-gray-700/50'
            }`}
          >
            {msg.content}
          </div>
        </div>
      ))}
    </>
  );
}

function TypingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="bg-gray-800/60 border border-gray-700/50 rounded-2xl px-3.5 py-2">
        <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
      </div>
    </div>
  );
}

function ChatInput({
  inputRef,
  input,
  setInput,
  loading,
  onSend,
}: {
  inputRef: React.RefObject<HTMLInputElement | null>;
  input: string;
  setInput: (v: string) => void;
  loading: boolean;
  onSend: () => void;
}) {
  return (
    <div className="flex-shrink-0 border-t border-gray-700/50 px-4 py-3 bg-gray-800/30">
      <form
        onSubmit={(e) => { e.preventDefault(); onSend(); }}
        className="flex items-center gap-2"
      >
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about your tasks..."
          className="flex-1 bg-gray-900/60 border border-gray-700/50 rounded-xl px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-transparent transition-all duration-200"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={!input.trim() || loading}
          className="p-2 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:from-indigo-700 hover:to-purple-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-200 shadow-lg shadow-indigo-500/20"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
}
