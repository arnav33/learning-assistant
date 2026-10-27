import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, ElementRef, OnDestroy, OnInit, computed, inject, signal, viewChild } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { ChatApi, ChatSession } from './chat-api';

@Component({
  imports: [CommonModule, ReactiveFormsModule],
  selector: 'app-chat',
  styleUrl: './chat.scss',
  templateUrl: './chat.html',
})
export class Chat implements OnInit, OnDestroy {
  private readonly chatApi = inject(ChatApi);
  private readonly transcript = viewChild<ElementRef<HTMLElement>>('transcript');

  readonly sessions = signal<ChatSession[]>([]);
  readonly selectedId = signal<string | null>(null);
  readonly loading = signal(false);
  readonly sending = signal(false);
  readonly errorMessage = signal('');
  readonly selected = computed(() => this.sessions().find((session) => session.id === this.selectedId()) ?? null);
  readonly groups = computed(() => {
    const byTopic = new Map<string, ChatSession[]>();
    for (const session of this.sessions()) {
      const grouped = byTopic.get(session.topic) ?? [];
      grouped.push(session);
      byTopic.set(session.topic, grouped);
    }
    return [...byTopic.entries()]
      .sort(([left], [right]) => left.localeCompare(right, undefined, { sensitivity: 'base' }))
      .map(([topic, sessions]) => ({
        topic,
        sessions: [...sessions].sort((left, right) => right.last_modified_time.localeCompare(left.last_modified_time)),
      }));
  });
  readonly expandedIds = signal<string[]>([]);
  private readonly spentSeconds = signal<Readonly<Record<string, number>>>({});
  private readonly thinkingSeconds = signal(0);
  private thinkingTimer: ReturnType<typeof setInterval> | null = null;
  readonly draft = new FormControl('', { nonNullable: true });
  readonly topic = new FormControl('', { nonNullable: true });

  ngOnInit(): void {
    this.loadSessions();
  }

  ngOnDestroy(): void {
    this.stopThinking();
  }

  loadSessions(): void {
    this.loading.set(true);
    this.errorMessage.set('');
    this.chatApi.getAll().subscribe({
      next: (sessions) => {
        const sorted = this.latestFirst(sessions);
        this.sessions.set(sorted);
        const selected = this.selectedId();
        if (!selected || !sorted.some((session) => session.id === selected)) {
          this.selectedId.set(sorted[0]?.id ?? null);
        }
        this.loading.set(false);
        this.scrollToLatest();
      },
      error: (error: HttpErrorResponse) => {
        this.sessions.set([]);
        this.loading.set(false);
        this.errorMessage.set(this.readError(error, 'Unable to load chats.'));
      },
    });
  }

  selectSession(sessionId: string): void {
    this.selectedId.set(sessionId);
    this.scrollToLatest();
  }

  startNewChat(): void {
    this.selectedId.set(null);
    this.draft.setValue('');
    this.topic.setValue('');
    this.errorMessage.set('');
  }

  displayText(chat: { message: string; compact?: string | null }): string {
    return chat.compact || chat.message;
  }

  thinkingLabel(): string {
    return `${Math.floor(this.thinkingSeconds())}s`;
  }

  spentLabel(chatId: string): string | null {
    const spent = this.spentSeconds()[chatId];
    if (spent == null) {
      return null;
    }
    return `${spent.toFixed(1)}s`;
  }

  linked(value: string): string {
    return value
      .split(/(<a\b[^>]*>.*?<\/a>)/gis)
      .map((part, index) => index % 2 === 1 ? part : this.linkify(part))
      .join('');
  }

  canExpand(chat: { message: string; compact?: string | null; detailed?: string | null }): boolean {
    return Boolean(chat.detailed) && chat.detailed !== this.displayText(chat);
  }

  expanded(chatId: string): boolean {
    return this.expandedIds().includes(chatId);
  }

  toggleAnswer(chatId: string): void {
    this.expandedIds.update((ids) => ids.includes(chatId) ? ids.filter((id) => id !== chatId) : [...ids, chatId]);
  }

  resultFields(item: Record<string, unknown>): { key: string; value: string }[] {
    return Object.entries(item).map(([key, value]) => ({ key, value: String(value ?? '') }));
  }

  topicLabel(topic: string): string {
    return topic.replace(/\S+/g, (word) => word.charAt(0).toUpperCase() + word.slice(1));
  }

  send(event?: Event): void {
    event?.preventDefault();
    const query = this.draft.value.trim();
    const chosenTopic = this.topic.value.trim();
    const sessionId = this.selectedId();
    if (!query || this.sending() || (!sessionId && !chosenTopic)) {
      return;
    }
    this.showOutgoing(sessionId, query, sessionId ? '' : chosenTopic);
    this.draft.setValue('');
    this.sending.set(true);
    this.errorMessage.set('');
    this.scrollToLatest();
    const sentAt = this.startThinking();
    this.chatApi.send(query, sessionId, sessionId ? null : chosenTopic).subscribe({
      next: (session) => {
        const spent = (Date.now() - sentAt) / 1000;
        this.stopThinking();
        const reply = [...session.chats].reverse().find((chat) => chat.sender === 'ai');
        if (reply) {
          this.spentSeconds.update((current) => ({ ...current, [reply.id]: spent }));
        }
        const rest = this.sessions().filter((item) => item.id !== session.id && item.id !== 'pending');
        this.sessions.set(this.latestFirst([session, ...rest]));
        this.selectedId.set(session.id);
        this.sending.set(false);
        this.scrollToLatest();
      },
      error: (error: HttpErrorResponse) => {
        this.stopThinking();
        this.sending.set(false);
        this.errorMessage.set(this.readError(error, 'Unable to send the message.'));
      },
    });
  }

  onComposerKeydown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.send();
    }
  }

  private startThinking(): number {
    const sentAt = Date.now();
    this.stopThinking();
    this.thinkingSeconds.set(0);
    this.thinkingTimer = setInterval(() => {
      this.thinkingSeconds.set((Date.now() - sentAt) / 1000);
    }, 1000);
    return sentAt;
  }

  private stopThinking(): void {
    if (this.thinkingTimer != null) {
      clearInterval(this.thinkingTimer);
      this.thinkingTimer = null;
    }
  }

  private linkify(value: string): string {
    const markdown = /\[([^\]\n]+)\]\((https?:\/\/[^\s)]+)\)/gi;
    const pieces: string[] = [];
    let last = 0;
    for (const match of value.matchAll(markdown)) {
      const index = match.index ?? 0;
      pieces.push(this.linkBare(value.slice(last, index)));
      pieces.push(this.anchor(match[2], match[1]));
      last = index + match[0].length;
    }
    pieces.push(this.linkBare(value.slice(last)));
    return pieces.join('');
  }

  private linkBare(value: string): string {
    return value.replace(/(^|[^"'=])(https?:\/\/[^\s<]+)/gi, (_match, prefix: string, url: string) => {
      const trimmed = url.replace(/[.,);:!?]+$/g, '');
      return `${prefix}${this.anchor(trimmed, trimmed)}${url.slice(trimmed.length)}`;
    });
  }

  private anchor(url: string, label: string): string {
    const href = url.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;');
    const text = label.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return `<a href="${href}">${text}</a>`;
  }

  private showOutgoing(sessionId: string | null, query: string, topic: string): void {
    const now = new Date().toISOString();
    const message = {
      id: crypto.randomUUID(),
      chat_session_id: sessionId ?? 'pending',
      sender: 'human' as const,
      message: query,
    };
    if (!sessionId) {
      const pending: ChatSession = {
        id: 'pending',
        name: query,
        topic,
        chats: [message],
        created_by: null,
        created_time: now,
        last_modified_by: null,
        last_modified_time: now,
      };
      this.sessions.set(this.latestFirst([pending, ...this.sessions()]));
      this.selectedId.set('pending');
      return;
    }
    this.sessions.set(this.latestFirst(this.sessions().map((session) => (
      session.id === sessionId
        ? { ...session, chats: [...session.chats, message], last_modified_time: now }
        : session
    ))));
  }

  private latestFirst(sessions: ChatSession[]): ChatSession[] {
    return [...sessions].sort((left, right) => right.last_modified_time.localeCompare(left.last_modified_time));
  }

  private scrollToLatest(): void {
    queueMicrotask(() => {
      const pane = this.transcript()?.nativeElement;
      if (pane) {
        pane.scrollTop = pane.scrollHeight;
      }
    });
  }

  private readError(error: HttpErrorResponse, fallback: string): string {
    const detail = error.error?.detail;
    if (typeof detail === 'string' && detail.length > 0) {
      return detail;
    }
    if (error.status === 0) {
      return 'Unable to reach the chat API.';
    }
    return fallback;
  }
}
