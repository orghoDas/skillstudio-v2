'use client';

import { useEffect, useState } from 'react';
import ChatRoomList from '@/components/ChatRoomList';

export default function ChatPage() {
  const [token, setToken] = useState('');

  useEffect(() => {
    // Get token from localStorage
    const storedToken = localStorage.getItem('access_token');
    if (storedToken) {
      setToken(storedToken);
    }
  }, []);

  if (!token) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Please log in to access chat
          </h2>
          <p className="text-gray-600">
            You need to be logged in to view and send messages
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <ChatRoomList token={token} />
    </div>
  );
}
