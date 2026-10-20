import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, ElementRef, OnInit, ViewChild, inject, signal } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { UtcToLocalPipe } from '../../shared/pipes/utc-to-local.pipe';
import { ModelApi, ModelRecord } from './model-api';

interface ModelForm {
  model: FormControl<string>;
  model_provider: FormControl<string>;
  thinking_budget: FormControl<number>;
  active: FormControl<boolean>;
}

@Component({
  imports: [CommonModule, ReactiveFormsModule, UtcToLocalPipe],
  selector: 'app-model',
  styleUrl: './model.scss',
  templateUrl: './model.html',
})
export class Model implements OnInit {
  private readonly modelApi = inject(ModelApi);

  @ViewChild('formModal') formModal!: ElementRef<HTMLDialogElement>;

  readonly records = signal<ModelRecord[]>([]);
  readonly loading = signal(false);
  readonly saving = signal(false);
  readonly errorMessage = signal('');
  readonly editingRecordId = signal<string | null>(null);
  private editingSnapshot: ModelRecord | null = null;

  form = new FormGroup<ModelForm>({
    model: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    model_provider: new FormControl('', { nonNullable: true, validators: [Validators.required] }),
    thinking_budget: new FormControl(0, { nonNullable: true, validators: [Validators.required, Validators.min(0)] }),
    active: new FormControl(true, { nonNullable: true }),
  });

  ngOnInit(): void {
    this.loadRecords();
  }

  loadRecords(): void {
    this.loading.set(true);
    this.errorMessage.set('');
    this.modelApi.getAll().subscribe({
      next: (records) => {
        this.records.set(records);
        this.loading.set(false);
      },
      error: (error: HttpErrorResponse) => {
        this.records.set([]);
        this.loading.set(false);
        this.errorMessage.set(this.readError(error, 'Unable to load models.'));
      },
    });
  }

  openAddModal(): void {
    this.editingRecordId.set(null);
    this.editingSnapshot = null;
    this.form.reset({
      model: '',
      model_provider: '',
      thinking_budget: 0,
      active: true,
    });
    this.formModal.nativeElement.showModal();
  }

  openEditModal(modelId: string): void {
    this.errorMessage.set('');
    this.modelApi.getById(modelId).subscribe({
      next: (record) => {
        if (!record) {
          this.errorMessage.set('Model not found.');
          return;
        }
        this.editingRecordId.set(record.id);
        this.editingSnapshot = record;
        this.form.setValue({
          model: record.model,
          model_provider: record.model_provider,
          thinking_budget: record.thinking_budget,
          active: record.active,
        });
        this.formModal.nativeElement.showModal();
      },
      error: (error: HttpErrorResponse) => {
        this.errorMessage.set(this.readError(error, 'Unable to load that model.'));
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
    if (editingId) {
      this.modelApi.update(editingId, record).subscribe({
        next: (updated) => this.finishSave(updated),
        error: (error: HttpErrorResponse) => this.failSave(error),
      });
      return;
    }

    this.modelApi.create(record).subscribe({
      next: () => this.finishSave(true),
      error: (error: HttpErrorResponse) => this.failSave(error),
    });
  }

  private finishSave(saved: boolean): void {
    this.saving.set(false);
    if (!saved) {
      this.errorMessage.set('The model API did not save this record.');
      return;
    }
    this.closeModal();
    this.loadRecords();
  }

  private failSave(error: HttpErrorResponse): void {
    this.saving.set(false);
    this.errorMessage.set(this.readError(error, 'Unable to save the model.'));
  }

  deleteRecord(modelId: string): void {
    if (!confirm('Are you sure you want to delete this record?')) {
      return;
    }

    this.errorMessage.set('');
    this.modelApi.delete(modelId).subscribe({
      next: (deleted) => {
        if (!deleted) {
          this.errorMessage.set('The model API did not delete this record.');
          return;
        }
        this.loadRecords();
      },
      error: (error: HttpErrorResponse) => {
        this.errorMessage.set(this.readError(error, 'Unable to delete the model.'));
      },
    });
  }

  private utcNow(): string {
    return new Date().toISOString();
  }

  private toRecord(): ModelRecord {
    const formData = this.form.getRawValue();
    const now = this.utcNow();
    const snapshot = this.editingSnapshot;

    return {
      id: snapshot?.id ?? crypto.randomUUID(),
      model: formData.model.trim(),
      model_provider: formData.model_provider.trim(),
      thinking_budget: Number(formData.thinking_budget),
      active: formData.active,
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
      return 'Unable to reach the model API.';
    }
    return fallback;
  }
}
