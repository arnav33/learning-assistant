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
    performance_reviews: 'search the notes and keep going well past the end of the visible line',
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
    const reviewsCell = fixture.nativeElement.querySelector('tbody tr td:nth-child(2)') as HTMLElement;
    const reviewText = reviewsCell.querySelector('.review-text') as HTMLElement;
    const viewButton = reviewsCell.querySelector('[aria-label="View performance reviews"]') as HTMLElement;
    expect(reviewText.textContent).toContain(sample.performance_reviews);
    expect(getComputedStyle(reviewText).whiteSpace).toBe('nowrap');
    expect(getComputedStyle(reviewText).textOverflow).toBe('ellipsis');
    expect(getComputedStyle(reviewText).overflow).toBe('hidden');
    expect(viewButton).not.toBeNull();
    expect(reviewText.compareDocumentPosition(viewButton) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    component.reviewsModal.nativeElement.showModal = () => undefined;
    reviewsCell.querySelector('button')?.dispatchEvent(new Event('click'));
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('.reviews').textContent).toContain(sample.performance_reviews);
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
    const promptInput = fixture.nativeElement.querySelector('#performance_reviews') as HTMLTextAreaElement;
    expect(nameInput.readOnly).toBe(true);
    expect(promptInput.value).toBe('');
    expect(fixture.nativeElement.querySelector('#active')).toBeNull();
    component.form.controls.description.setValue('writes lessons');
    component.form.controls.performance_reviews.setValue('answer from the library');
    component.onSave();

    const request = http.expectOne(`/api/v1/core/agents/${sample.id}`);
    expect(request.request.method).toBe('PUT');
    expect(request.request.body.model_id).toBe(model.id);
    expect(request.request.body.name).toBe('local14');
    expect(request.request.body.performance_reviews).toBe(`${sample.performance_reviews}\nanswer from the library`);
    expect(request.request.body.active).toBe(true);
    request.flush(true);
    flushLoads();
  });
});
