import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

export interface ChatMessage {
  id: string;
  chat_session_id: string;
  sender: 'human' | 'ai';
  message: string;
  results?: Record<string, unknown>[] | null;
  compact?: string | null;
  detailed?: string | null;
  codes?: string | null;
  references?: string[] | null;
}

export interface ChatSession {
  id: string;
  name: string;
  topic: string;
  chats: ChatMessage[];
  created_by: string | null;
  created_time: string;
  last_modified_by: string | null;
  last_modified_time: string;
}

@Injectable({ providedIn: 'root' })
export class ChatApi {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = '/api/v1/chat';

  getAll(): Observable<ChatSession[]> {
    return this.http.get<ChatSession[]>(`${this.baseUrl}/`);
  }

  send(query: string, sessionId: string | null, topic: string | null): Observable<ChatSession> {
    return this.http.post<ChatSession>(`${this.baseUrl}/chat`, {
      query,
      session_id: sessionId,
      topic,
    });
  }
}
