import { writable, derived, get, type Writable, type Readable } from 'svelte/store';

export interface PaneTabState {
  id: string;
  paneId: string;
  title: string;
  componentType: string;
  componentProps?: Record<string, any>;
  isActive: boolean;
  isPinned: boolean;
  order: number;
  isCloseable: boolean;
}

/**
 * PaneTab represents a tab within a pane that displays a specific component
 */
export class PaneTab {
  private _state: Writable<PaneTabState>;

  // Derived stores for easy access
  public readonly id: Readable<string>;
  public readonly paneId: Readable<string>;
  public readonly title: Readable<string>;
  public readonly componentType: Readable<string>;
  public readonly componentProps: Readable<Record<string, any>>;
  public readonly isActive: Readable<boolean>;
  public readonly isPinned: Readable<boolean>;
  public readonly order: Readable<number>;
  public readonly isCloseable: Readable<boolean>;

  // PaneComponent instance (will be set by PaneTabManager)
  public paneComponent: any = null;

  constructor(
    id: string,
    paneId: string,
    title: string,
    componentType: string,
    componentProps: Record<string, any> = {},
    order: number = 0,
    isCloseable: boolean = true
  ) {
    this._state = writable({
      id,
      paneId,
      title,
      componentType,
      componentProps,
      isActive: false,
      isPinned: false,
      order,
      isCloseable
    });

    // Derived stores
    this.id = derived(this._state, $state => $state.id);
    this.paneId = derived(this._state, $state => $state.paneId);
    this.title = derived(this._state, $state => $state.title);
    this.componentType = derived(this._state, $state => $state.componentType);
    this.componentProps = derived(this._state, $state => $state.componentProps || {});
    this.isActive = derived(this._state, $state => $state.isActive);
    this.isPinned = derived(this._state, $state => $state.isPinned);
    this.order = derived(this._state, $state => $state.order);
    this.isCloseable = derived(this._state, $state => $state.isCloseable);
  }

  /**
   * Get the current state synchronously
   */
  getState(): PaneTabState {
    return get(this._state);
  }

  /**
   * Set the tab as active
   */
  setActive(active: boolean): void {
    this._state.update(s => ({
      ...s,
      isActive: active
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
   * Update component props
   */
  setComponentProps(props: Record<string, any>): void {
    this._state.update(s => ({
      ...s,
      componentProps: { ...s.componentProps, ...props }
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
  subscribe(callback: (state: PaneTabState) => void) {
    return this._state.subscribe(callback);
  }

  /**
   * Export tab state for serialization
   */
  toJSON(): PaneTabState {
    return get(this._state);
  }

  /**
   * Create tab from JSON
   */
  static fromJSON(json: PaneTabState): PaneTab {
    const tab = new PaneTab(
      json.id,
      json.paneId,
      json.title,
      json.componentType,
      json.componentProps || {},
      json.order,
      json.isCloseable
    );

    if (json.isPinned) {
      tab.setPinned(true);
    }

    if (json.isActive) {
      tab.setActive(true);
    }

    return tab;
  }
}
