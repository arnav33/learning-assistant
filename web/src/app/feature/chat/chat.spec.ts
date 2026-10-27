import { vi } from 'vitest';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { Chat } from './chat';
import { ChatSession } from './chat-api';

describe('Chat', () => {
  let fixture: ComponentFixture<Chat>;
  let http: HttpTestingController;

  const older: ChatSession = {
    id: 'older',
    name: 'what is a cell',
    topic: 'cells',
    chats: [
      { id: 'o1', chat_session_id: 'older', sender: 'human', message: 'what is a cell' },
      { id: 'o2', chat_session_id: 'older', sender: 'ai', message: 'A cell is the basic unit of life.' },
    ],
    created_by: null,
    created_time: '2026-10-20T00:00:00.000Z',
    last_modified_by: null,
    last_modified_time: '2026-10-20T00:00:00.000Z',
  };

  const newerCells: ChatSession = {
    id: 'newer-cells',
    name: 'what is mitochondria',
    topic: 'cells',
    chats: [
      { id: 'n1', chat_session_id: 'newer-cells', sender: 'human', message: 'what is mitochondria' },
      { id: 'n2', chat_session_id: 'newer-cells', sender: 'ai', message: 'Mitochondria make energy.' },
    ],
    created_by: null,
    created_time: '2026-10-21T06:00:00.000Z',
    last_modified_by: null,
    last_modified_time: '2026-10-21T06:00:00.000Z',
  };

  const latest: ChatSession = {
    id: 'latest',
    name: 'what is langchain in python',
    topic: 'python libraries',
    chats: [
      { id: 'l1', chat_session_id: 'latest', sender: 'human', message: 'what is langchain in python' },
      { id: 'l2', chat_session_id: 'latest', sender: 'ai', message: 'LangChain is a Python library.' },
    ],
    created_by: null,
    created_time: '2026-10-22T00:00:00.000Z',
    last_modified_by: null,
    last_modified_time: '2026-10-22T00:00:00.000Z',
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Chat],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();

    fixture = TestBed.createComponent(Chat);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    http.verify();
    vi.restoreAllMocks();
    vi.useRealTimers();
  });

  function flushSessions(sessions: ChatSession[]): void {
    fixture.detectChanges();
    http.expectOne('/api/v1/chat/').flush(sessions);
    fixture.detectChanges();
  }

  it('groups sessions by topic and shows the topic above the conversation', () => {
    flushSessions([older, latest, newerCells]);

    const headings = [...fixture.nativeElement.querySelectorAll('.topic-group h3')].map((heading: HTMLElement) => heading.textContent?.trim());
    const labels = [...fixture.nativeElement.querySelectorAll('.session')].map((button: HTMLButtonElement) => button.textContent?.trim());
    expect(headings).toEqual(['Cells', 'Python Libraries']);
    expect(labels).toEqual([
      'what is mitochondria',
      'what is a cell',
      'what is langchain in python',
    ]);
    expect(fixture.nativeElement.querySelector('.session.selected').textContent).toContain('what is langchain in python');
    expect(fixture.nativeElement.querySelector('.conversation-topic').textContent).toContain('Python Libraries');
    expect(fixture.nativeElement.querySelector('input.topic')).toBeNull();
  });

  it('shows the selected session with the latest message last', () => {
    flushSessions([latest]);

    const messages = [...fixture.nativeElement.querySelectorAll('.message')].map((item: HTMLElement) => item.textContent?.trim());
    expect(messages).toEqual(['what is langchain in python', 'LangChain is a Python library.']);
    expect(fixture.nativeElement.querySelector('.message.human')).toBeTruthy();
    expect(fixture.nativeElement.querySelector('.message.ai')).toBeTruthy();
  });

  it('sends the query for the selected session', () => {
    flushSessions([latest]);
    fixture.componentInstance.draft.setValue('what is a chain');
    fixture.detectChanges();
    vi.useFakeTimers();
    let now = 1_000;
    vi.spyOn(Date, 'now').mockImplementation(() => now);
    fixture.debugElement.query(By.css('form')).triggerEventHandler('submit');
    fixture.detectChanges();

    let messages = [...fixture.nativeElement.querySelectorAll('.message')].map((item: HTMLElement) => item.textContent?.trim());
    expect(messages.at(-1)).toBe('what is a chain');
    expect(fixture.nativeElement.querySelector('.pending').textContent).toContain('Thinking…');
    expect(fixture.nativeElement.querySelector('.pending .elapsed').textContent).toBe('0s');
    now = 2_000;
    vi.advanceTimersByTime(1_000);
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('.pending .elapsed').textContent).toBe('1s');
    expect(fixture.componentInstance.draft.value).toBe('');

    const request = http.expectOne('/api/v1/chat/chat');
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual({ query: 'what is a chain', session_id: 'latest', topic: null });
    now = 4_200;
    request.flush({
      ...latest,
      last_modified_time: '2026-10-21T01:00:00.000Z',
      chats: [
        ...latest.chats,
        { id: 'l3', chat_session_id: 'latest', sender: 'human', message: 'what is a chain' },
        { id: 'l4', chat_session_id: 'latest', sender: 'ai', message: 'A chain calls one step after another.' },
      ],
    });
    fixture.detectChanges();

    messages = [...fixture.nativeElement.querySelectorAll('.message')].map((item: HTMLElement) => item.textContent?.trim());
    expect(messages.at(-1)).toContain('A chain calls one step after another.');
    expect(fixture.nativeElement.querySelector('.elapsed').textContent).toBe('3.2s');
    expect(fixture.nativeElement.querySelector('.pending')).toBeNull();
    expect(fixture.componentInstance.draft.value).toBe('');
  });

  it('asks for a topic once when starting a chat', () => {
    flushSessions([]);
    fixture.componentInstance.startNewChat();
    fixture.detectChanges();

    const topic = fixture.nativeElement.querySelector('.topic') as HTMLInputElement;
    expect(topic).toBeTruthy();
    fixture.componentInstance.draft.setValue('what is python');
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('button[type="submit"]').disabled).toBe(true);

    fixture.componentInstance.topic.setValue('snakes');
    fixture.detectChanges();
    fixture.debugElement.query(By.css('form')).triggerEventHandler('submit');
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('input.topic')).toBeNull();
    expect(fixture.nativeElement.querySelector('.conversation-topic').textContent).toContain('Snakes');
    expect(fixture.nativeElement.querySelector('.topic-group h3').textContent).toContain('Snakes');
    expect(fixture.nativeElement.querySelector('.session').textContent?.trim()).toBe('what is python');

    const request = http.expectOne('/api/v1/chat/chat');
    expect(request.request.body).toEqual({ query: 'what is python', session_id: null, topic: 'snakes' });
    request.flush({
      id: 'created',
      name: 'what is python',
      topic: 'snakes',
      chats: [
        { id: 'c1', chat_session_id: 'created', sender: 'human', message: 'what is python' },
        { id: 'c2', chat_session_id: 'created', sender: 'ai', message: 'what is python' },
      ],
      created_by: null,
      created_time: '2026-10-21T02:00:00.000Z',
      last_modified_by: null,
      last_modified_time: '2026-10-21T02:00:00.000Z',
    });
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('input.topic')).toBeNull();
    expect(fixture.nativeElement.querySelector('.conversation-topic').textContent).toContain('Snakes');
    expect(fixture.componentInstance.selected()?.topic).toBe('snakes');
  });

  it('shows the synthesized answer without the search fields', () => {
    flushSessions([{
      ...latest,
      chats: [
        latest.chats[0],
        {
          id: 'l2',
          chat_session_id: 'latest',
          sender: 'ai',
          message: 'LangChain is a framework for language model apps.',
          results: [
            { rank: 1, title: 'LangChain', href: 'https://example.com/langchain', body: 'A library.' },
            { rank: 2, title: 'Python', href: 'https://example.com/python', body: 'A language.' },
          ],
        },
      ],
    }]);

    const answer = fixture.nativeElement.querySelector('.message.ai p') as HTMLElement;
    expect(answer.textContent).toContain('LangChain is a framework for language model apps.');
    expect(fixture.nativeElement.querySelector('.search-results')).toBeNull();
  });

  it('shows the compact answer and expands the full answer', () => {
    flushSessions([{
      ...latest,
      chats: [
        latest.chats[0],
        {
          id: 'l2',
          chat_session_id: 'latest',
          sender: 'ai',
          message: 'A framework.',
          compact: 'A framework.',
          answer: 'LangChain is a framework for building applications with large language models.',
        },
      ],
    }]);

    const shown = fixture.nativeElement.querySelector('.message.ai .answer-line p') as HTMLElement;
    expect(shown.textContent).toContain('A framework.');
    expect(fixture.nativeElement.querySelector('.full-answer')).toBeNull();
    fixture.nativeElement.querySelector('.expand').click();
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('.full-answer').textContent).toContain('large language models');
  });

  it('shows references under the expanded answer', () => {
    flushSessions([{
      ...latest,
      chats: [
        latest.chats[0],
        {
          id: 'l2',
          chat_session_id: 'latest',
          sender: 'ai',
          message: 'Yes.',
          compact: 'Yes.',
          answer: 'You can write AI agents in Java.',
          references: ['[ADK for Java](https://example.com/adk)'],
        },
      ],
    }]);

    fixture.nativeElement.querySelector('.expand').click();
    fixture.detectChanges();
    const link = fixture.nativeElement.querySelector('.references a') as HTMLAnchorElement;
    expect(fixture.nativeElement.querySelector('.full-answer').textContent).toContain('You can write AI agents in Java.');
    expect(link.getAttribute('href')).toBe('https://example.com/adk');
    expect(link.textContent).toBe('ADK for Java');
  });

  it('shows a sanitized hyperlink in the full answer', () => {
    flushSessions([{
      ...latest,
      chats: [
        latest.chats[0],
        {
          id: 'l2',
          chat_session_id: 'latest',
          sender: 'ai',
          message: 'A framework.',
          compact: 'A framework.',
          answer: 'LangChain is a framework [docs](https://example.com/langchain). <script>alert(1)</script><a href="javascript:alert(1)">bad</a>',
        },
      ],
    }]);

    fixture.nativeElement.querySelector('.expand').click();
    fixture.detectChanges();
    const links = [...fixture.nativeElement.querySelectorAll('.full-answer a')] as HTMLAnchorElement[];
    expect(links[0].getAttribute('href')).toBe('https://example.com/langchain');
    expect(links[0].textContent).toBe('docs');
    expect(links.some((item) => (item.getAttribute('href') ?? '').startsWith('javascript:'))).toBe(false);
    expect(fixture.nativeElement.querySelector('.full-answer script')).toBeNull();
  });
});
