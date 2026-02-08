'use client';

import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';

interface ChatContextType {
  isOpen: boolean;
  threadId: string | null;
  toggleChat: () => void;
  openChat: () => void;
  closeChat: () => void;
  startNewChat: () => void;
  setThreadId: (id: string) => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider = ({ children }: { children: ReactNode }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [threadId, setThreadIdState] = useState<string | null>(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('chatkit_thread_id');
    }
    return null;
  });

  const toggleChat = useCallback(() => {
    setIsOpen((prev) => !prev);
  }, []);

  const openChat = useCallback(() => {
    setIsOpen(true);
  }, []);

  const closeChat = useCallback(() => {
    setIsOpen(false);
  }, []);

  const startNewChat = useCallback(() => {
    setThreadIdState(null);
    if (typeof window !== 'undefined') {
      localStorage.removeItem('chatkit_thread_id');
    }
  }, []);

  const setThreadId = useCallback((id: string) => {
    setThreadIdState(id);
    if (typeof window !== 'undefined') {
      localStorage.setItem('chatkit_thread_id', id);
    }
  }, []);

  const value = {
    isOpen,
    threadId,
    toggleChat,
    openChat,
    closeChat,
    startNewChat,
    setThreadId,
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};
