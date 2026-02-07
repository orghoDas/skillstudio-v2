'use client';

import React, { useState, useEffect } from 'react';
import { MessageCircle, Users, Clock, Search } from 'lucide-react';
import { chatService, ChatRoom } from '@/lib/chat-service';
import ChatInterface from './ChatInterface';

interface ChatRoomListProps {
  token: string;
}

export default function ChatRoomList({ token }: ChatRoomListProps) {
  const [rooms, setRooms] = useState<ChatRoom[]>([]);
  const [selectedRoom, setSelectedRoom] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRooms();
  }, []);

  const loadRooms = async () => {
    try {
      setLoading(true);
      const { rooms: loadedRooms } = await chatService.getRooms();
      setRooms(loadedRooms);
    } catch (error) {
      console.error('Error loading rooms:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredRooms = rooms.filter((room) =>
    room.name?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getRoomIcon = (type: ChatRoom['room_type']) => {
    switch (type) {
      case 'DIRECT':
        return <MessageCircle className="w-5 h-5" />;
      case 'COURSE':
        return <Users className="w-5 h-5" />;
      case 'LIVE_CLASS':
        return <Clock className="w-5 h-5" />;
      case 'GROUP':
        return <Users className="w-5 h-5" />;
      default:
        return <MessageCircle className="w-5 h-5" />;
    }
  };

  const getRoomTypeLabel = (type: ChatRoom['room_type']) => {
    switch (type) {
      case 'DIRECT':
        return 'Direct Message';
      case 'COURSE':
        return 'Course Discussion';
      case 'LIVE_CLASS':
        return 'Live Class';
      case 'GROUP':
        return 'Group Chat';
      default:
        return type;
    }
  };

  if (selectedRoom) {
    return (
      <ChatInterface
        roomId={selectedRoom}
        token={token}
        onClose={() => setSelectedRoom(null)}
      />
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Chat Rooms</h2>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search rooms..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Room List */}
      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading rooms...</p>
        </div>
      ) : filteredRooms.length === 0 ? (
        <div className="text-center py-12">
          <MessageCircle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-600">
            {searchQuery ? 'No rooms found' : 'No chat rooms yet'}
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {filteredRooms.map((room) => (
            <button
              key={room.id}
              onClick={() => setSelectedRoom(room.id)}
              className="w-full flex items-center gap-4 p-4 hover:bg-gray-50 rounded-lg transition-colors text-left"
            >
              <div className="p-3 bg-blue-100 text-blue-600 rounded-full">
                {getRoomIcon(room.room_type)}
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-gray-900 truncate">
                  {room.name || getRoomTypeLabel(room.room_type)}
                </h3>
                <p className="text-sm text-gray-500">
                  {getRoomTypeLabel(room.room_type)}
                </p>
              </div>
              <div className="flex items-center gap-2">
                {room.is_active && (
                  <div className="w-2 h-2 bg-green-500 rounded-full" />
                )}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
