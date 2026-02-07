'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Send, Paperclip, Smile, MoreVertical, X } from 'lucide-react';
import { chatService, ChatMessage, ChatRoom } from '@/lib/chat-service';
import wsService from '@/lib/websocket-service';

interface ChatInterfaceProps {
  roomId: string;
  token: string;
  onClose?: () => void;
}

export default function ChatInterface({ roomId, token, onClose }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [typingUsers, setTypingUsers] = useState<Set<string>>(new Set());
  const [room, setRoom] = useState<ChatRoom | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    // Load room details
    loadRoom();

    // Load initial messages
    loadMessages();

    // Connect to WebSocket
    connectWebSocket();

    return () => {
      // Cleanup on unmount
      wsService.disconnect();
    };
  }, [roomId]);

  useEffect(() => {
    // Scroll to bottom when new messages arrive
    scrollToBottom();
  }, [messages]);

  const loadRoom = async () => {
    try {
      const roomData = await chatService.getRoom(roomId);
      setRoom(roomData);
    } catch (error) {
      console.error('Error loading room:', error);
    }
  };

  const loadMessages = async () => {
    try {
      const { messages: loadedMessages } = await chatService.getMessages(roomId);
      setMessages(loadedMessages);
    } catch (error) {
      console.error('Error loading messages:', error);
    }
  };

  const connectWebSocket = async () => {
    try {
      await wsService.connect(roomId, token);
      setIsConnected(true);

      // Register message handlers
      wsService.on('new_message', handleNewMessage);
      wsService.on('user_typing', handleUserTyping);
      wsService.on('user_joined', handleUserJoined);
      wsService.on('user_left', handleUserLeft);
      wsService.on('message_deleted', handleMessageDeleted);

    } catch (error) {
      console.error('Error connecting to WebSocket:', error);
      setIsConnected(false);
    }
  };

  const handleNewMessage = (data: any) => {
    const newMessage: ChatMessage = {
      id: data.message_id,
      room_id: data.room_id,
      sender_id: data.sender_id,
      message_type: data.message_type,
      content: data.content,
      metadata: data.metadata || {},
      is_edited: false,
      is_deleted: false,
      created_at: data.created_at,
    };

    setMessages((prev) => [...prev, newMessage]);
  };

  const handleUserTyping = (data: any) => {
    if (data.is_typing) {
      setTypingUsers((prev) => new Set(prev).add(data.user_id));
    } else {
      setTypingUsers((prev) => {
        const next = new Set(prev);
        next.delete(data.user_id);
        return next;
      });
    }
  };

  const handleUserJoined = (data: any) => {
    // Could show a system message or notification
    console.log(`User ${data.user_id} joined`);
  };

  const handleUserLeft = (data: any) => {
    // Could show a system message or notification
    console.log(`User ${data.user_id} left`);
  };

  const handleMessageDeleted = (data: any) => {
    setMessages((prev) =>
      prev.map((msg) =>
        msg.id === data.message_id
          ? { ...msg, is_deleted: true, deleted_at: data.deleted_at }
          : msg
      )
    );
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    try {
      // Send via WebSocket for instant delivery
      wsService.sendMessage(inputMessage.trim());

      // Clear input
      setInputMessage('');

      // Stop typing indicator
      if (isTyping) {
        wsService.sendTyping(false);
        setIsTyping(false);
      }
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputMessage(e.target.value);

    // Send typing indicator
    if (!isTyping) {
      wsService.sendTyping(true);
      setIsTyping(true);
    }

    // Clear existing timeout
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }

    // Set new timeout to stop typing indicator
    typingTimeoutRef.current = setTimeout(() => {
      wsService.sendTyping(false);
      setIsTyping(false);
    }, 3000);
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b bg-gray-50">
        <div>
          <h3 className="font-semibold text-gray-900">
            {room?.name || 'Chat Room'}
          </h3>
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
            <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button className="p-2 hover:bg-gray-200 rounded-lg transition-colors">
            <MoreVertical className="w-5 h-5 text-gray-600" />
          </button>
          {onClose && (
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-gray-600" />
            </button>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.sender_id === token ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[70%] rounded-lg px-4 py-2 ${
                message.sender_id === token
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-900'
              } ${message.is_deleted ? 'opacity-50 italic' : ''}`}
            >
              {message.is_deleted ? (
                <p className="text-sm">Message deleted</p>
              ) : (
                <>
                  <p className="break-words">{message.content}</p>
                  <p
                    className={`text-xs mt-1 ${
                      message.sender_id === token ? 'text-blue-100' : 'text-gray-500'
                    }`}
                  >
                    {formatTime(message.created_at)}
                  </p>
                </>
              )}
            </div>
          </div>
        ))}

        {/* Typing indicator */}
        {typingUsers.size > 0 && (
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <div className="flex gap-1">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
            <span>Someone is typing...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t p-4">
        <div className="flex items-center gap-2">
          <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <Paperclip className="w-5 h-5 text-gray-600" />
          </button>
          <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <Smile className="w-5 h-5 text-gray-600" />
          </button>
          <input
            type="text"
            value={inputMessage}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            placeholder="Type a message..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={!isConnected}
          />
          <button
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || !isConnected}
            className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
