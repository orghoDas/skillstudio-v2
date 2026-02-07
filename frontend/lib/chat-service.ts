/**
 * Chat service for managing chat rooms and messages
 */

import { api } from './api';

export interface ChatRoom {
  id: string;
  name?: string;
  room_type: 'DIRECT' | 'COURSE' | 'LIVE_CLASS' | 'GROUP';
  course_id?: string;
  is_active: boolean;
  max_participants?: number;
  metadata: any;
  created_at: string;
  updated_at?: string;
}

export interface ChatMessage {
  id: string;
  room_id: string;
  sender_id: string;
  message_type: 'TEXT' | 'IMAGE' | 'FILE' | 'CODE' | 'SYSTEM';
  content: string;
  metadata: any;
  is_edited: boolean;
  edited_at?: string;
  is_deleted: boolean;
  deleted_at?: string;
  reply_to_id?: string;
  created_at: string;
}

export interface ChatParticipant {
  id: string;
  room_id: string;
  user_id: string;
  joined_at: string;
  last_read_at?: string;
  is_online: boolean;
  is_muted: boolean;
}

export interface CreateChatRoomData {
  name?: string;
  room_type: ChatRoom['room_type'];
  course_id?: string;
  max_participants?: number;
  participant_ids?: string[];
  metadata?: any;
}

export interface SendMessageData {
  content: string;
  message_type?: ChatMessage['message_type'];
  reply_to_id?: string;
  metadata?: any;
}

class ChatService {
  /**
   * Create a new chat room
   */
  async createRoom(data: CreateChatRoomData): Promise<ChatRoom> {
    const response = await api.post('/chat/rooms', data);
    return response.data;
  }

  /**
   * Get all chat rooms for current user
   */
  async getRooms(skip = 0, limit = 50): Promise<{
    rooms: ChatRoom[];
    total: number;
    skip: number;
    limit: number;
  }> {
    const response = await api.get('/chat/rooms', {
      params: { skip, limit },
    });
    return response.data;
  }

  /**
   * Get a specific chat room
   */
  async getRoom(roomId: string): Promise<ChatRoom> {
    const response = await api.get(`/chat/rooms/${roomId}`);
    return response.data;
  }

  /**
   * Send a message to a chat room
   */
  async sendMessage(roomId: string, data: SendMessageData): Promise<ChatMessage> {
    const response = await api.post(`/chat/rooms/${roomId}/messages`, data);
    return response.data;
  }

  /**
   * Get messages from a chat room
   */
  async getMessages(
    roomId: string,
    skip = 0,
    limit = 50,
    before?: string
  ): Promise<{
    messages: ChatMessage[];
    total: number;
    skip: number;
    limit: number;
  }> {
    const response = await api.get(`/chat/rooms/${roomId}/messages`, {
      params: { skip, limit, before },
    });
    return response.data;
  }

  /**
   * Get participants in a chat room
   */
  async getParticipants(roomId: string): Promise<ChatParticipant[]> {
    const response = await api.get(`/chat/rooms/${roomId}/participants`);
    return response.data;
  }

  /**
   * Delete a message
   */
  async deleteMessage(roomId: string, messageId: string): Promise<void> {
    await api.delete(`/chat/rooms/${roomId}/messages/${messageId}`);
  }

  /**
   * Create or get a direct message room with another user
   */
  async getOrCreateDirectRoom(userId: string): Promise<ChatRoom> {
    // First, try to find existing direct room
    const { rooms } = await this.getRooms(0, 100);
    const existingRoom = rooms.find(
      (room) => room.room_type === 'DIRECT' && room.metadata?.user_id === userId
    );

    if (existingRoom) {
      return existingRoom;
    }

    // Create new direct room
    return this.createRoom({
      room_type: 'DIRECT',
      participant_ids: [userId],
      metadata: { user_id: userId },
    });
  }

  /**
   * Get or create a course discussion room
   */
  async getOrCreateCourseRoom(courseId: string): Promise<ChatRoom> {
    const { rooms } = await this.getRooms(0, 100);
    const existingRoom = rooms.find(
      (room) => room.room_type === 'COURSE' && room.course_id === courseId
    );

    if (existingRoom) {
      return existingRoom;
    }

    return this.createRoom({
      name: 'Course Discussion',
      room_type: 'COURSE',
      course_id: courseId,
    });
  }
}

export const chatService = new ChatService();
export default chatService;
