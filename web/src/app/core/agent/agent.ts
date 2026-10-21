import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, ElementRef, OnInit, ViewChild, inject, signal } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { forkJoin } from 'rxjs';
import { UtcToLocalPipe } from '../../shared/pipes/utc-to-local.pipe';
import { ModelApi, ModelRecord } from '../model/model-api';
import { AgentApi, AgentRecord } from './agent-api';

interface AgentForm {
  name: FormControl<string>;
  model_id: FormControl<string>;
  description: FormControl<string>;
}

@Component({
  imports: [CommonModule, ReactiveFormsModule, UtcToLocalPipe],
  selector: 'app-agent',
  styleUrl: './agent.scss',
  templateUrl: './agent.html',
})
export class Agent implements OnInit {
  private readonly agentApi = inject(AgentApi);
  private readonly modelApi = inject(ModelApi);

  @ViewChild('formModal') formModal!: ElementRef<HTMLDialogElement>;

  readonly records = signal<AgentRecord[]>([]);
  readonly models = signal<ModelRecord[]>([]);
  readonly loading = signal(false);
  readonly saving = signal(false);
  readonly errorMessage = signal('');
  readonly editingRecordId = signal<string | null>(null);
  private editingSnapshot: AgentRecord | null = null;

  form = new FormGroup<AgentForm>({
    name: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    model_id: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    description: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
  });

  ngOnInit(): void {
    this.loadRecords();
  }

  loadRecords(): void {
    this.loading.set(true);
    this.errorMessage.set('');
    forkJoin({
      agents: this.agentApi.getAll(),
      models: this.modelApi.getAll(),
    }).subscribe({
      next: ({ agents, models }) => {
        this.records.set(agents);
        this.models.set(models);
        this.loading.set(false);
      },
      error: (error: HttpErrorResponse) => {
        this.records.set([]);
        this.models.set([]);
        this.loading.set(false);
        this.errorMessage.set(this.readError(error, 'Unable to load agents.'));
      },
    });
  }

  modelFor(modelId: string): ModelRecord | undefined {
    return this.models().find((model) => model.id === modelId);
  }

  openEditModal(agentId: string): void {
    this.errorMessage.set('');
    this.agentApi.getById(agentId).subscribe({
      next: (record) => {
        if (!record) {
          this.errorMessage.set('Agent not found.');
          return;
        }
        this.editingRecordId.set(record.id);
        this.editingSnapshot = record;
        this.form.setValue({
          name: record.name,
          model_id: record.model_id,
          description: record.description,
        });
        this.formModal.nativeElement.showModal();
      },
      error: (error: HttpErrorResponse) => {
        this.errorMessage.set(this.readError(error, 'Unable to load that agent.'));
      },
    });
  }

  closeModal(): void {
    this.saving.set(false);
    this.formModal.nativeElement.close();
  }

  onSave(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const record = this.toRecord();
    this.saving.set(true);
    this.errorMessage.set('');

    const editingId = this.editingRecordId();
    if (!editingId) {
      this.saving.set(false);
      return;
    }

    this.agentApi.update(editingId, record).subscribe({
      next: (updated) => this.finishSave(updated),
      error: (error: HttpErrorResponse) => this.failSave(error),
    });
  }

  private finishSave(saved: boolean): void {
    this.saving.set(false);
    if (!saved) {
      this.errorMessage.set('The agent API did not save this record.');
      return;
    }
    this.closeModal();
    this.loadRecords();
  }

  private failSave(error: HttpErrorResponse): void {
    this.saving.set(false);
    this.errorMessage.set(this.readError(error, 'Unable to save the agent.'));
  }

  private utcNow(): string {
    return new Date().toISOString();
  }

  private toRecord(): AgentRecord {
    const formData = this.form.getRawValue();
    const now = this.utcNow();
    const snapshot = this.editingSnapshot;

    return {
      id: snapshot?.id ?? crypto.randomUUID(),
      name: snapshot?.name ?? formData.name.trim(),
      description: formData.description.trim(),
      model_id: formData.model_id,
      active: true,
      created_by: null,
      created_time: snapshot?.created_time ?? now,
      last_modified_by: null,
      last_modified_time: now,
    };
  }

  private readError(error: HttpErrorResponse, fallback: string): string {
    const detail = error.error?.detail;
    if (typeof detail === 'string' && detail.length > 0) {
      return detail;
    }
    if (error.status === 0) {
      return 'Unable to reach the agent API.';
    }
    return fallback;
  }
}
