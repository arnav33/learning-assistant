import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { UtcToLocalPipe } from '../../shared/pipes/utc-to-local.pipe';
import { Model } from './model';
import { ModelRecord } from './model-api';

describe('Model', () => {
  let component: Model;
  let fixture: ComponentFixture<Model>;
  let http: HttpTestingController;

  const sample: ModelRecord = {
    id: 'model-1',
    model: 'gpt-4o',
    model_provider: 'openai',
    thinking_budget: 0,
    active: true,
    created_by: null,
    created_time: '2026-10-20T00:00:00.000Z',
    last_modified_by: null,
    last_modified_time: '2026-10-20T00:00:00.000Z',
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Model],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();

    fixture = TestBed.createComponent(Model);
    component = fixture.componentInstance;
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    http.verify();
  });

  it('should create', () => {
    fixture.detectChanges();
    http.expectOne('/api/v1/core/models/').flush([]);

    expect(component).toBeTruthy();
  });

  it('should list models returned by the api', async () => {
    fixture.detectChanges();
    const request = http.expectOne('/api/v1/core/models/');
    expect(request.request.method).toBe('GET');
    request.flush([sample]);
    await fixture.whenStable();
    fixture.detectChanges();

    expect(component.loading()).toBe(false);
    expect(component.records()).toEqual([sample]);
    expect(fixture.nativeElement.textContent).toContain('gpt-4o');
    expect(fixture.nativeElement.textContent).toContain('openai');
    expect(fixture.nativeElement.textContent).toContain(new UtcToLocalPipe().transform(sample.last_modified_time));
    expect(fixture.nativeElement.textContent).not.toContain(sample.last_modified_time);
  });
});
