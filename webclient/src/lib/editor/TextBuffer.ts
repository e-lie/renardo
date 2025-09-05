import { writable, derived, get, type Writable, type Readable } from 'svelte/store';

export interface BufferMetadata {
  id: number;
  name: string;
  language?: string;
  readonly?: boolean;
  isStartupFile?: boolean;
  filePath?: string;
  source?: 'manual' | 'tutorial' | 'music-example' | 'session' | 'file';
  createdAt: Date;
  modifiedAt: Date;
}

export interface BufferState {
  content: string;
  metadata: BufferMetadata;
  dirty: boolean;
  version: number;
}

/**
 * TextBuffer manages the content and metadata of a single text/code unit
 * It's independent of any UI representation (tabs)
 */
export class TextBuffer {
  private _state: Writable<BufferState>;
  public readonly content: Readable<string>;
  public readonly metadata: Readable<BufferMetadata>;
  public readonly dirty: Readable<boolean>;
  
  private _history: string[] = [];
  private _historyIndex = -1;
  private _maxHistorySize = 50;

  constructor(metadata: Partial<BufferMetadata>, initialContent = '') {
    const now = new Date();
    const fullMetadata: BufferMetadata = {
      id: metadata.id || Date.now(),
      name: metadata.name || 'Untitled',
      language: metadata.language || 'python',
      readonly: metadata.readonly || false,
      isStartupFile: metadata.isStartupFile || false,
      filePath: metadata.filePath,
      source: metadata.source || 'manual',
      createdAt: metadata.createdAt || now,
      modifiedAt: now
    };

    this._state = writable({
      content: initialContent,
      metadata: fullMetadata,
      dirty: false,
      version: 0
    });

    // Derived stores for easy access
    this.content = derived(this._state, $state => $state.content);
    this.metadata = derived(this._state, $state => $state.metadata);
    this.dirty = derived(this._state, $state => $state.dirty);

    // Initialize history
    this._addToHistory(initialContent);
  }

  /**
   * Update buffer content
   */
  setContent(newContent: string): void {
    const state = get(this._state);
    
    // Don't update if readonly
    if (state.metadata.readonly) {
      console.warn(`Buffer "${state.metadata.name}" is readonly`);
      return;
    }

    // Don't update if content hasn't changed
    if (state.content === newContent) {
      return;
    }

    this._state.update(s => ({
      ...s,
      content: newContent,
      dirty: true,
      version: s.version + 1,
      metadata: {
        ...s.metadata,
        modifiedAt: new Date()
      }
    }));

    this._addToHistory(newContent);
  }

  /**
   * Get current content synchronously
   */
  getContent(): string {
    return get(this._state).content;
  }

  /**
   * Get metadata synchronously
   */
  getMetadata(): BufferMetadata {
    return get(this._state).metadata;
  }

  /**
   * Mark buffer as clean (saved)
   */
  markClean(): void {
    this._state.update(s => ({
      ...s,
      dirty: false
    }));
  }

  /**
   * Update metadata
   */
  updateMetadata(updates: Partial<BufferMetadata>): void {
    this._state.update(s => ({
      ...s,
      metadata: {
        ...s.metadata,
        ...updates,
        modifiedAt: new Date()
      }
    }));
  }

  /**
   * Rename buffer
   */
  rename(newName: string): void {
    this.updateMetadata({ name: newName });
  }

  /**
   * Undo last change
   */
  undo(): boolean {
    if (this._historyIndex > 0) {
      this._historyIndex--;
      const content = this._history[this._historyIndex];
      
      this._state.update(s => ({
        ...s,
        content,
        dirty: true,
        version: s.version + 1
      }));
      
      return true;
    }
    return false;
  }

  /**
   * Redo last undone change
   */
  redo(): boolean {
    if (this._historyIndex < this._history.length - 1) {
      this._historyIndex++;
      const content = this._history[this._historyIndex];
      
      this._state.update(s => ({
        ...s,
        content,
        dirty: true,
        version: s.version + 1
      }));
      
      return true;
    }
    return false;
  }

  /**
   * Check if buffer matches content
   */
  matchesContent(name: string, content: string): boolean {
    const state = get(this._state);
    return state.metadata.name === name && state.content === content;
  }

  /**
   * Subscribe to state changes
   */
  subscribe(callback: (state: BufferState) => void) {
    return this._state.subscribe(callback);
  }

  /**
   * Add content to history for undo/redo
   */
  private _addToHistory(content: string): void {
    // Remove any history after current index
    this._history = this._history.slice(0, this._historyIndex + 1);
    
    // Add new content
    this._history.push(content);
    
    // Limit history size
    if (this._history.length > this._maxHistorySize) {
      this._history.shift();
    } else {
      this._historyIndex++;
    }
  }

  /**
   * Export buffer state for serialization
   */
  toJSON(): any {
    const state = get(this._state);
    return {
      content: state.content,
      metadata: state.metadata
    };
  }

  /**
   * Create buffer from JSON
   */
  static fromJSON(json: any): TextBuffer {
    return new TextBuffer(json.metadata, json.content);
  }
}