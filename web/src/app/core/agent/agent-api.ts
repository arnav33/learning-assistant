import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

export interface AgentRecord {
  id: string;
  name: string;
  description: string;
  model_id: string;
  active: boolean;
  created_by: string | null;
  created_time: string;
  last_modified_by: string | null;
  last_modified_time: string;
}

@Injectable({ providedIn: 'root' })
export class AgentApi {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = '/api/v1/core/agents';

  getAll(): Observable<AgentRecord[]> {
    return this.http.get<AgentRecord[]>(`${this.baseUrl}/`);
  }

  getById(agentId: string): Observable<AgentRecord | null> {
    return this.http.get<AgentRecord | null>(`${this.baseUrl}/${agentId}`);
  }

  create(agent: AgentRecord): Observable<string> {
    return this.http.post<string>(`${this.baseUrl}/`, agent);
  }

  update(agentId: string, agent: AgentRecord): Observable<boolean> {
    return this.http.put<boolean>(`${this.baseUrl}/${agentId}`, agent);
  }

  delete(agentId: string): Observable<boolean> {
    return this.http.delete<boolean>(`${this.baseUrl}/${agentId}`);
  }
}
