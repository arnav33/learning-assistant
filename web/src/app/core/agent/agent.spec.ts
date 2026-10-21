import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { UtcToLocalPipe } from '../../shared/pipes/utc-to-local.pipe';
import { ModelRecord } from '../model/model-api';
import { Agent } from './agent';
import { AgentRecord } from './agent-api';

describe('Agent', () => {
  let component: Agent;
  let fixture: ComponentFixture<Agent>;
  let http: HttpTestingController;

  const model: ModelRecord = {
    id: 'model-1',
    model: 'gpt-4o',
    model_provider: 'openai',
    thinking_budget: 3,
    active: true,
    created_by: null,
    created_time: '2026-10-20T00:00:00.000Z',
    last_modified_by: null,
    last_modified_time: '2026-10-20T00:00:00.000Z',
  };

  const sample: AgentRecord = {
    id: 'agent-1',
    name: 'local14',
    description: 'local agent',
    model_id: 'model-1',
    active: false,
    created_by: null,
    created_time: '2026-10-20T00:00:00.000Z',
    last_modified_by: null,
    last_modified_time: '2026-10-20T00:00:00.000Z',
  };

  function flushLoads(agents: AgentRecord[] = [], models: ModelRecord[] = []): void {
    http.expectOne('/api/v1/core/agents/').flush(agents);
    http.expectOne('/api/v1/core/models/').flush(models);
  }

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Agent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();

    fixture = TestBed.createComponent(Agent);
    component = fixture.componentInstance;
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    http.verify();
  });

  it('should create', () => {
    fixture.detectChanges();
    flushLoads();

    expect(component).toBeTruthy();
  });

  it('should list agents with the selected model details', async () => {
    fixture.detectChanges();
    const agentsRequest = http.expectOne('/api/v1/core/agents/');
    const modelsRequest = http.expectOne('/api/v1/core/models/');
    expect(agentsRequest.request.method).toBe('GET');
    expect(modelsRequest.request.method).toBe('GET');
    agentsRequest.flush([sample]);
    modelsRequest.flush([model]);
    await fixture.whenStable();
    fixture.detectChanges();

    const text = fixture.nativeElement.textContent;
    expect(component.loading()).toBe(false);
    expect(component.records()).toEqual([sample]);
    expect(text).not.toContain('Add New Agent');
    expect(fixture.nativeElement.querySelector('[aria-label="Delete"]')).toBeNull();
    expect(text).toContain('local14');
    expect(text).toContain('gpt-4o');
    expect(text).toContain('openai');
    expect(text).toContain('3');
    expect(text).toContain('No');
    expect(text).toContain(new UtcToLocalPipe().transform(sample.last_modified_time));
    expect(text).not.toContain(sample.last_modified_time);
  });

  it('should keep the agent name when saving an edit', () => {
    fixture.detectChanges();
    flushLoads([sample], [model]);
    component.formModal.nativeElement.showModal = () => undefined;
    component.formModal.nativeElement.close = () => undefined;

    component.openEditModal(sample.id);
    http.expectOne(`/api/v1/core/agents/${sample.id}`).flush(sample);
    fixture.detectChanges();

    const nameInput = fixture.nativeElement.querySelector('#name') as HTMLInputElement;
    expect(nameInput.readOnly).toBe(true);
    expect(fixture.nativeElement.querySelector('#active')).toBeNull();
    component.form.controls.description.setValue('writes lessons');
    component.onSave();

    const request = http.expectOne(`/api/v1/core/agents/${sample.id}`);
    expect(request.request.method).toBe('PUT');
    expect(request.request.body.model_id).toBe(model.id);
    expect(request.request.body.name).toBe('local14');
    expect(request.request.body.active).toBe(true);
    request.flush(true);
    flushLoads();
  });
});
