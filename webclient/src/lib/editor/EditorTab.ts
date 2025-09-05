import { writable, derived, get, type Writable, type Readable } from 'svelte/store';

export interface TabState {
  id: number;
  bufferId: number;
  title: string;
  isEditing: boolean;
  isPinned: boolean;
  order: number;
}

/**
 * EditorTab represents a UI frame/viewport displaying a TextBuffer
 * Multiple tabs can display the same buffer (split view)
 */
export class EditorTab {
  private _state: Writable<TabState>;
  public readonly id: Readable<number>;
  public readonly bufferId: Readable<number>;
  public readonly title: Readable<string>;
  public readonly isEditing: Readable<boolean>;
  public readonly isPinned: Readable<boolean>;

  constructor(id: number, bufferId: number, title: string, order: number = 0) {
    this._state = writable({
      id,
      bufferId,
      title,
      isEditing: false,
      isPinned: false,
      order
    });

    // Derived stores for easy access
    this.id = derived(this._state, $state => $state.id);
    this.bufferId = derived(this._state, $state => $state.bufferId);
    this.title = derived(this._state, $state => $state.title);
    this.isEditing = derived(this._state, $state => $state.isEditing);
    this.isPinned = derived(this._state, $state => $state.isPinned);
  }

  /**
   * Get the current state synchronously
   */
  getState(): TabState {
    return get(this._state);
  }

  /**
   * Update the buffer this tab is displaying
   */
  setBufferId(bufferId: number): void {
    this._state.update(s => ({
      ...s,
      bufferId
    }));
  }

  /**
   * Update the tab title
   */
  setTitle(title: string): void {
    this._state.update(s => ({
      ...s,
      title
    }));
  }

  /**
   * Start editing the tab title
   */
  startEditing(): void {
    this._state.update(s => ({
      ...s,
      isEditing: true
    }));
  }

  /**
   * Stop editing the tab title
   */
  stopEditing(): void {
    this._state.update(s => ({
      ...s,
      isEditing: false
    }));
  }

  /**
   * Toggle pinned state
   */
  togglePin(): void {
    this._state.update(s => ({
      ...s,
      isPinned: !s.isPinned
    }));
  }

  /**
   * Set pinned state
   */
  setPinned(pinned: boolean): void {
    this._state.update(s => ({
      ...s,
      isPinned: pinned
    }));
  }

  /**
   * Update the order (for tab reordering)
   */
  setOrder(order: number): void {
    this._state.update(s => ({
      ...s,
      order
    }));
  }

  /**
   * Subscribe to state changes
   */
  subscribe(callback: (state: TabState) => void) {
    return this._state.subscribe(callback);
  }

  /**
   * Export tab state for serialization
   */
  toJSON(): TabState {
    return get(this._state);
  }

  /**
   * Create tab from JSON
   */
  static fromJSON(json: TabState): EditorTab {
    const tab = new EditorTab(json.id, json.bufferId, json.title, json.order);
    if (json.isPinned) {
      tab.setPinned(true);
    }
    return tab;
  }
}