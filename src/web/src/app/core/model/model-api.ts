import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

export interface ModelRecord {
  id: string;
  model: string;
  model_provider: string;
  thinking_budget: number;
  active: boolean;
  created_by: string | null;
  created_time: string;
  last_modified_by: string | null;
  last_modified_time: string;
}

@Injectable({ providedIn: 'root' })
export class ModelApi {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = '/api/v1/service/models';

  getAll(): Observable<ModelRecord[]> {
    return this.http.get<ModelRecord[]>(`${this.baseUrl}/`);
  }

  getById(modelId: string): Observable<ModelRecord | null> {
    return this.http.get<ModelRecord | null>(`${this.baseUrl}/${modelId}`);
  }

  create(model: ModelRecord): Observable<string> {
    return this.http.post<string>(`${this.baseUrl}/`, model);
  }

  update(modelId: string, model: ModelRecord): Observable<boolean> {
    return this.http.put<boolean>(`${this.baseUrl}/${modelId}`, model);
  }

  delete(modelId: string): Observable<boolean> {
    return this.http.delete<boolean>(`${this.baseUrl}/${modelId}`);
  }
}
