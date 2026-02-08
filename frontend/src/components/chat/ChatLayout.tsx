'use client';

import { useAuth } from '@/contexts/AuthContext';
import { ChatProvider } from '@/contexts/ChatContext';
import ChatFAB from './ChatFAB';
import ChatPanel from './ChatPanel';

export default function ChatLayout() {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) return null;

  return (
    <ChatProvider>
      <ChatFAB />
      <ChatPanel />
    </ChatProvider>
  );
}
