import { writable, derived, get, type Writable, type Readable } from 'svelte/store';
import { TextBuffer, type BufferMetadata } from './TextBuffer';
import { EditorTab } from './EditorTab';

export interface TabManagerState {
  buffers: Map<number, TextBuffer>;
  tabs: Map<number, EditorTab>;
  activeTabId: number | null;
  nextBufferId: number;
  nextTabId: number;
  isTabSwitching: boolean;
}

export interface CreateTabOptions {
  title?: string;
  content?: string;
  source?: 'manual' | 'tutorial' | 'music-example' | 'session' | 'file';
  language?: string;
  filePath?: string;
  isStartupFile?: boolean;
}

/**
 * TabManager coordinates EditorTabs and TextBuffers
 * Handles the relationship between UI tabs and content buffers
 */
export class TabManager {
  private _state: Writable<TabManagerState>;
  
  // Derived stores for external use
  public readonly activeTab: Readable<EditorTab | null>;
  public readonly activeBuffer: Readable<TextBuffer | null>;
  public readonly tabs: Readable<EditorTab[]>;
  public readonly buffers: Readable<TextBuffer[]>;
  public readonly startupBuffer: Readable<TextBuffer | null>;

  constructor() {
    this._state = writable({
      buffers: new Map(),
      tabs: new Map(),
      activeTabId: null,
      nextBufferId: 1,
      nextTabId: 1,
      isTabSwitching: false
    });

    // Derived stores
    this.activeTab = derived(this._state, $state => 
      $state.activeTabId ? $state.tabs.get($state.activeTabId) || null : null
    );

    this.activeBuffer = derived(this._state, $state => {
      if (!$state.activeTabId) return null;
      const tab = $state.tabs.get($state.activeTabId);
      if (!tab) return null;
      const tabState = tab.getState();
      return $state.buffers.get(tabState.bufferId) || null;
    });

    this.tabs = derived(this._state, $state => 
      Array.from($state.tabs.values()).sort((a, b) => 
        a.getState().order - b.getState().order
      )
    );

    this.buffers = derived(this._state, $state => 
      Array.from($state.buffers.values())
    );

    this.startupBuffer = derived(this._state, $state => {
      for (const buffer of $state.buffers.values()) {
        if (buffer.getMetadata().isStartupFile) {
          return buffer;
        }
      }
      return null;
    });

    // Ensure startup buffer exists
    this.ensureStartupBuffer();
  }

  /**
   * Ensure a startup buffer always exists
   */
  private ensureStartupBuffer(): void {
    const state = get(this._state);
    let startupBuffer: TextBuffer | null = null;

    // Check if we already have a startup buffer
    for (const buffer of state.buffers.values()) {
      if (buffer.getMetadata().isStartupFile) {
        startupBuffer = buffer;
        break;
      }
    }

    if (!startupBuffer) {
      // Create startup buffer
      startupBuffer = new TextBuffer(
        {
          id: 1,
          name: 'startup.py',
          isStartupFile: true,
          source: 'manual',
          readonly: false
        },
        '# Renardo startup file\n# This file is loaded when Renardo starts\n# Add your custom code here\n'
      );

      // Create tab for startup buffer
      const startupTab = new EditorTab(1, 1, 'startup.py', 0);

      this._state.update(s => ({
        ...s,
        buffers: new Map(s.buffers).set(1, startupBuffer!),
        tabs: new Map(s.tabs).set(1, startupTab),
        activeTabId: 1,
        nextBufferId: Math.max(2, s.nextBufferId),
        nextTabId: Math.max(2, s.nextTabId)
      }));
    }
  }

  /**
   * Create a new tab with a new buffer
   */
  createTab(options: CreateTabOptions = {}): number {
    const state = get(this._state);
    
    const bufferId = state.nextBufferId;
    const tabId = state.nextTabId;
    
    // Create new buffer
    const buffer = new TextBuffer(
      {
        id: bufferId,
        name: options.title || `Untitled-${bufferId}`,
        language: options.language || 'python',
        source: options.source || 'manual',
        filePath: options.filePath,
        isStartupFile: options.isStartupFile || false
      },
      options.content || ''
    );

    // Create new tab
    const tab = new EditorTab(
      tabId,
      bufferId,
      options.title || `Untitled-${bufferId}`,
      state.tabs.size
    );

    this._state.update(s => ({
      ...s,
      buffers: new Map(s.buffers).set(bufferId, buffer),
      tabs: new Map(s.tabs).set(tabId, tab),
      activeTabId: tabId,
      nextBufferId: bufferId + 1,
      nextTabId: tabId + 1
    }));

    return tabId;
  }

  /**
   * Load content into a new tab or switch to existing
   */
  loadContent(name: string, content: string, source: CreateTabOptions['source'] = 'manual'): number {
    const state = get(this._state);

    // Check if we already have this exact content
    for (const buffer of state.buffers.values()) {
      if (buffer.matchesContent(name, content)) {
        // Find tab displaying this buffer
        for (const tab of state.tabs.values()) {
          if (tab.getState().bufferId === buffer.getMetadata().id) {
            this.switchToTab(tab.getState().id);
            return tab.getState().id;
          }
        }
      }
    }

    // Create new tab with this content
    return this.createTab({
      title: name,
      content,
      source
    });
  }

  /**
   * Switch to a specific tab
   */
  switchToTab(tabId: number, callback?: () => void): void {
    const state = get(this._state);
    
    if (!state.tabs.has(tabId)) {
      console.error(`Tab ${tabId} not found`);
      return;
    }

    if (state.activeTabId === tabId) {
      callback?.();
      return;
    }

    // Set switching flag
    this._state.update(s => ({
      ...s,
      isTabSwitching: true,
      activeTabId: tabId
    }));

    // Reset flag after delay
    setTimeout(() => {
      this._state.update(s => ({
        ...s,
        isTabSwitching: false
      }));
      callback?.();
    }, 200);
  }

  /**
   * Close a tab
   */
  closeTab(tabId: number): boolean {
    const state = get(this._state);
    const tab = state.tabs.get(tabId);
    
    if (!tab) return false;
    
    const tabState = tab.getState();
    const buffer = state.buffers.get(tabState.bufferId);
    
    // Can't close startup tab
    if (buffer && buffer.getMetadata().isStartupFile) {
      console.warn('Cannot close startup tab');
      return false;
    }

    // Check if this is the last tab showing this buffer
    let bufferStillUsed = false;
    for (const [otherTabId, otherTab] of state.tabs) {
      if (otherTabId !== tabId && otherTab.getState().bufferId === tabState.bufferId) {
        bufferStillUsed = true;
        break;
      }
    }

    // Remove tab
    const newTabs = new Map(state.tabs);
    newTabs.delete(tabId);

    // Remove buffer if no longer used
    const newBuffers = new Map(state.buffers);
    if (!bufferStillUsed) {
      newBuffers.delete(tabState.bufferId);
    }

    // Determine new active tab
    let newActiveTabId = state.activeTabId;
    if (state.activeTabId === tabId) {
      // Find startup tab first
      for (const [id, tab] of newTabs) {
        const buffer = state.buffers.get(tab.getState().bufferId);
        if (buffer?.getMetadata().isStartupFile) {
          newActiveTabId = id;
          break;
        }
      }
      // If no startup tab, use first available
      if (newActiveTabId === tabId && newTabs.size > 0) {
        newActiveTabId = newTabs.keys().next().value;
      }
    }

    this._state.update(s => ({
      ...s,
      tabs: newTabs,
      buffers: newBuffers,
      activeTabId: newActiveTabId
    }));

    return true;
  }

  /**
   * Update content of the active buffer
   */
  updateActiveBufferContent(content: string): void {
    const state = get(this._state);
    if (!state.activeTabId) return;
    
    const tab = state.tabs.get(state.activeTabId);
    if (!tab) return;
    
    const buffer = state.buffers.get(tab.getState().bufferId);
    if (!buffer) return;
    
    buffer.setContent(content);
  }

  /**
   * Get active buffer content
   */
  getActiveBufferContent(): string {
    const buffer = get(this.activeBuffer);
    return buffer ? buffer.getContent() : '';
  }

  /**
   * Check if tab switching is in progress
   */
  isTabSwitching(): boolean {
    return get(this._state).isTabSwitching;
  }

  /**
   * Save session to JSON
   */
  toJSON(): any {
    const state = get(this._state);
    return {
      buffers: Array.from(state.buffers.entries()).map(([id, buffer]) => ({
        id,
        data: buffer.toJSON()
      })),
      tabs: Array.from(state.tabs.entries()).map(([id, tab]) => ({
        id,
        data: tab.toJSON()
      })),
      activeTabId: state.activeTabId,
      nextBufferId: state.nextBufferId,
      nextTabId: state.nextTabId
    };
  }

  /**
   * Load session from JSON
   */
  static fromJSON(json: any): TabManager {
    const manager = new TabManager();
    
    const buffers = new Map<number, TextBuffer>();
    const tabs = new Map<number, EditorTab>();
    
    // Load buffers
    for (const { id, data } of json.buffers) {
      buffers.set(id, TextBuffer.fromJSON(data));
    }
    
    // Load tabs
    for (const { id, data } of json.tabs) {
      tabs.set(id, EditorTab.fromJSON(data));
    }
    
    manager._state.set({
      buffers,
      tabs,
      activeTabId: json.activeTabId,
      nextBufferId: json.nextBufferId,
      nextTabId: json.nextTabId,
      isTabSwitching: false
    });
    
    return manager;
  }

  /**
   * Subscribe to state changes
   */
  subscribe(callback: (state: TabManagerState) => void) {
    return this._state.subscribe(callback);
  }
}